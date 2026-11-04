"""Standalone, read-only catalog access. Python 3.11+, standard library only."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
MAX_BYTES = 64 * 1024 * 1024


class LibraryError(ValueError):
    def __init__(self, category, message):
        super().__init__(message)
        self.category = category


def load_registry(path=None):
    path = path or REPO_ROOT / 'library/library-registry.json'
    return json.loads(Path(path).read_text(encoding='utf-8'))


def all_text_bodies(source):
    bodies = source.get('text_bodies', [])
    if bodies:
        return bodies
    if source.get('text_status') in {'available', 'verified'} and source.get('text_location'):
        body = {k: v for k, v in source.items() if k.startswith('text_') or k in
                {'language', 'translator', 'editor', 'edition_label', 'license_status', 'license_notes',
                 'mediation', 'mediation_type', 'translator_status', 'editor_status'}}
        body.update(body_id=source['source_id'], work_title=source['title'], status=source['text_status'])
        return [body]
    return []


def select(registry, source_id, body_id=None):
    sources = [s for s in registry['sources'] if s['source_id'] == source_id]
    if len(sources) != 1:
        raise LibraryError('unknown-source', 'Require one registered source identity')
    source = sources[0]
    if body_id is None:
        return source
    bodies = [b for b in all_text_bodies(source) if b['body_id'] == body_id]
    if len(bodies) != 1:
        raise LibraryError('unknown-body', 'Require one body belonging to this source')
    return source, bodies[0]


def resolve_root(explicit=None, repo=REPO_ROOT):
    value = explicit or os.environ.get('MIRA_LIBRARY_TEXT_ROOT')
    if not value:
        raise LibraryError('unconfigured', 'Supply --text-root or MIRA_LIBRARY_TEXT_ROOT')
    root = Path(value).expanduser().resolve()
    if root.is_relative_to(Path(repo).resolve()):
        raise LibraryError('invalid-root', 'Archive storage must be outside this checkout')
    if not root.is_dir():
        raise LibraryError('invalid-root', 'Archive root must be an existing directory')
    return root


def verified_bytes(body, root, repo=REPO_ROOT):
    if body.get('status', body.get('text_status')) not in {'available', 'verified'}:
        raise LibraryError('unavailable', 'Body is not admitted as available or verified')
    root = resolve_root(root, repo)
    uri = body.get('text_location', '')
    if not uri.startswith('library-text://'):
        raise LibraryError('invalid-location', 'Require a logical library-text URI')
    relative = uri[len('library-text://'):]
    if not relative or ':' in relative or '\\' in relative or any(x in {'', '.', '..'} for x in relative.split('/')):
        raise LibraryError('invalid-location', 'Unsafe logical body location')
    path = (root / relative).resolve()
    if not path.is_relative_to(root) or path.is_relative_to(Path(repo).resolve()):
        raise LibraryError('invalid-location', 'Body escapes external archive storage')
    try:
        with path.open('rb') as stream:
            data = stream.read(MAX_BYTES + 1)
    except FileNotFoundError as error:
        raise LibraryError('missing', 'Registered body is absent from this archive') from error
    except OSError as error:
        raise LibraryError('unavailable', 'Registered body cannot be read') from error
    if len(data) > MAX_BYTES:
        raise LibraryError('oversized', 'Body exceeds the 64 MiB snapshot limit')
    digest = hashlib.sha256(data).hexdigest()
    if digest != body.get('text_sha256') or len(data) != body.get('text_bytes'):
        raise LibraryError('hash-mismatch', 'Body digest or size differs from the catalog')
    return path, data, digest


def verify(registry, root, source_id=None, body_id=None):
    root = resolve_root(root)
    sources = [select(registry, source_id)] if source_id else registry['sources']
    results = []
    if body_id and not source_id:
        raise LibraryError('invalid-request', '--body requires --source')
    for source in sources:
        bodies = all_text_bodies(source)
        if body_id:
            bodies = [select(registry, source['source_id'], body_id)[1]]
        if not bodies:
            results.append({'source_id': source['source_id'], 'status': 'unavailable'})
        for body in bodies:
            row = {'source_id': source['source_id'], 'body_id': body['body_id']}
            try:
                _, _, digest = verified_bytes(body, root)
                row.update(status='verified', sha256=digest)
            except LibraryError as error:
                row.update(status=error.category, message=str(error))
            results.append(row)
    failures = [r for r in results if r['status'] not in {'verified', 'unavailable'}]
    counts = {key: sum(r['status'] == key for r in results) for key in sorted({r['status'] for r in results})}
    return {'status': 'failed' if failures else 'ok', 'counts': counts,
            'metadata_only_sources': sum('body_id' not in r for r in results),
            'unavailable_bodies': sum(r['status'] == 'unavailable' and 'body_id' in r for r in results),
            'results': results}
