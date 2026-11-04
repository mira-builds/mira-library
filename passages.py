"""Read-only, snapshot-bound Library passages. Historical extractors stay unchanged."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import unicodedata
import xml.etree.ElementTree as ET

import catalog as library

MAX_BYTES = 64 * 1024 * 1024
MAX_EXCERPT = 2400
VERSION = 'library-passage-v1'
PAGE = re.compile(r'^\s*(?:#{1,6}\s*|---\s*)?\[?PDF page\s+(\d+)\]?(?:\s*---)?\s*$', re.I | re.M)


class PassageError(ValueError):
    def __init__(self, category, message):
        super().__init__(message)
        self.category = category


def normalized(value):
    return unicodedata.normalize('NFC', value).casefold()


def query_terms(value):
    terms = re.findall(r'[^\W_]+(?:-[^\W_]+)*', normalized(value), re.UNICODE)
    if value.strip() and not terms:
        raise PassageError('invalid-query', 'Query contains no searchable letters or numbers')
    return terms


TEXT_ROOT = None

@dataclass(frozen=True)
class Snapshot:
    source: dict
    body: dict
    path: Path
    data: bytes
    sha256: str


def snapshot(source_id, body_id, repo=library.REPO_ROOT):
    source, body = library.select(library.load_registry(repo / 'library/library-registry.json'), source_id, body_id)
    path, data, digest = library.verified_bytes(body, TEXT_ROOT, repo)
    return Snapshot(source, body, path, data, digest)


def units(snap):
    try:
        text = snap.data.decode(snap.body.get('text_encoding') or 'utf-8').lstrip('\ufeff')
    except (UnicodeError, LookupError) as error:
        raise PassageError('unsupported', 'Body cannot be decoded using its registered encoding') from error
    clean = lambda value: re.sub(r'\s+', ' ', value).strip()
    rows = []
    if snap.path.suffix.lower() in {'.xml', '.tei'}:
        if re.search(r'<!\s*(?:DOCTYPE|ENTITY)\b', text, re.I):
            raise PassageError('unsupported', 'XML document type and entity declarations are unsupported')
        try:
            root = ET.fromstring(text)
        except ET.ParseError as error:
            raise PassageError('unsupported', 'Malformed XML body') from error
        body = next((n for n in root.iter() if n.tag.rsplit('}', 1)[-1] == 'body'), None)
        if body is None:
            raise PassageError('unsupported', 'XML requires an explicit text body')
        def walk(node, section=''):
            name = node.tag.rsplit('}', 1)[-1]
            if name in {'p', 'ab', 'l'}:
                value = clean(''.join(node.itertext()))
                if value:
                    rows.append({'text': value, 'structure': {'element': name, 'n': node.get('n'), 'xml_id': node.get('{http://www.w3.org/XML/1998/namespace}id'), 'section': section}})
                return
            for child in node:
                if child.tag.rsplit('}', 1)[-1] == 'head':
                    section = clean(''.join(child.itertext()))[:200]
                else:
                    walk(child, section)
        walk(body)
    elif snap.path.suffix.lower() in {'.txt', '.md', '.text'}:
        # Retained PDF markers are structural; do not present them as source prose.
        markers = list(PAGE.finditer(text))
        sections = [(None, text)] if not markers else [(int(m[1]), text[m.end():markers[i + 1].start() if i + 1 < len(markers) else len(text)]) for i, m in enumerate(markers)]
        publishing = False
        for page, section in sections:
            for raw in re.split(r'\n\s*\n', section):
                value = clean(raw)
                if re.search(r'END OF (?:THE |THIS )?PROJECT GUTENBERG|FULL PROJECT GUTENBERG LICENSE', value, re.I):
                    publishing = True
                if not value:
                    continue
                excluded = publishing or bool(re.search(r'Project Gutenberg|^Mira Library derived text|^Source sha256:|^Source: https?://|^Repository: |^License posture: |^Recovered for Mira Library', value, re.I))
                rows.append({'text': value, 'structure': {'paragraph': len(rows) + 1, **({'pdf_page': page} if page is not None else {})}, 'excluded': excluded})
    else:
        raise PassageError('unsupported', 'Use an admitted text extraction for binary or unsupported formats')
    return rows


def sentence_spans(value):
    # Deliberately conservative: abbreviations need human review; no claim of linguistic parsing.
    ends = [m.end() for m in re.finditer(r'(?:[.!?][\"”’\']*(?:\s+|$)|[。！？][\"”’\']*\s*)', value)]
    starts = [0] + ends
    if not ends or ends[-1] < len(value):
        ends.append(len(value))
    return [(a + len(value[a:b]) - len(value[a:b].lstrip()), b - len(value[a:b]) + len(value[a:b].rstrip())) for a, b in zip(starts, ends) if value[a:b].strip()]


def read(source_id, body_id, *, query=None, locator=None, repo=library.REPO_ROOT):
    if (query is None) == (locator is None):
        raise PassageError('invalid-request', 'Supply exactly one query or locator')
    terms = query_terms(query) if query is not None else []
    if query is not None and not terms:
        raise PassageError('invalid-query', 'Passage retrieval requires a nonempty query')
    snap = snapshot(source_id, body_id, repo)
    rows = units(snap)
    selected = []
    diagnostics = []
    if locator is not None:
        if not isinstance(locator, dict) or locator.get('version') != VERSION:
            raise PassageError('unsupported-locator', 'Require a locator returned by this passage reader; historical readers remain available')
        if locator.get('source_sha256') != snap.sha256 or locator.get('source_id') != source_id or locator.get('body_id') != body_id:
            raise PassageError('locator-mismatch', 'Locator belongs to different source bytes or identity')
        i, a, b = (locator.get(k) for k in ('unit', 'start', 'end'))
        if not all(type(n) is int for n in (i, a, b)) or not 0 <= i < len(rows) or not 0 <= a < b <= len(rows[i]['text']) or b - a > MAX_EXCERPT:
            raise PassageError('invalid-locator', 'Invalid or unbounded passage span')
        if hashlib.sha256(rows[i]['text'][a:b].encode()).hexdigest() != locator.get('excerpt_sha256'):
            raise PassageError('locator-mismatch', 'Exact passage digest mismatch')
        spans = [(0, len(rows[i]['text']))] if rows[i]['structure'].get('element') == 'l' else sentence_spans(rows[i]['text'])
        if a not in {start for start, _ in spans} or b not in {end for _, end in spans}:
            raise PassageError('invalid-locator', 'Exact span must retain sentence or verse boundaries')
        selected = [(i, a, b)]
    else:
        candidates = []
        for i, row in enumerate(rows):
            if row.get('excluded'):
                continue
            spans = [(0, len(row['text']))] if row['structure'].get('element') == 'l' else sentence_spans(row['text'])
            scored = [(sum(t in normalized(row['text'][a:b]) for t in terms), a, b) for a, b in spans]
            hits = [s for s in scored if s[0]]
            if not hits:
                continue
            score, a, b = max(hits, key=lambda s: (s[0], -s[1]))
            if b - a > MAX_EXCERPT:
                diagnostics.append({'unit': i, 'status': 'narrowing-required', 'reason': 'Matching sentence or verse exceeds excerpt limit'})
                continue
            candidates.append((score, i, a, b))
        selected = [(i, a, b) for _, i, a, b in sorted(candidates, key=lambda r: (-r[0], r[1]))[:2]]
    passages = []
    for i, a, b in selected:
        row = rows[i]
        excerpt = row['text'][a:b]
        digest = hashlib.sha256(excerpt.encode()).hexdigest()
        loc = {'version': VERSION, 'source_id': source_id, 'body_id': body_id, 'source_sha256': snap.sha256, 'unit': i, 'start': a, 'end': b, 'excerpt_sha256': digest}
        passages.append({'source_id': source_id, 'body_id': body_id, 'source_sha256': snap.sha256,
                         'edition': snap.body.get('edition_label') or snap.source.get('edition_label') or '',
                         'language': snap.body.get('language') or snap.source.get('language') or '',
                         'translator': snap.body.get('translator'), 'extraction_version': VERSION,
                         'locator': loc, 'structure': row['structure'], 'excerpt_sha256': digest,
                         'text': excerpt, 'context_before': row['text'][max(0, a - 300):a] or (rows[i - 1]['text'][-300:] if i and not rows[i - 1].get('excluded') else ''),
                         'context_after': row['text'][b:b + 300] or (rows[i + 1]['text'][:300] if i + 1 < len(rows) and not rows[i + 1].get('excluded') else ''), 'context_may_be_partial': True,
                         'ref': snap.body['text_location'], 'boundary': json.dumps(row['structure'], ensure_ascii=False) + f'; characters {a}:{b}'})
    return {'status': 'ok' if passages else ('narrowing-required' if diagnostics else 'no-match'),
            'source_id': source_id, 'body_id': body_id, 'source_sha256': snap.sha256,
            'passages': passages, 'diagnostics': diagnostics, 'writes_performed': False,
            'review_required': 'Check sentence completeness, relevance, quotation rights, and the original PDF for tables, figures, or equations.'}
