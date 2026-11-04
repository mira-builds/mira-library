"""Validate public shelf proposals as data; never download, admit or execute them."""
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

PATTERN = re.compile(r'contributions/([a-z0-9]+(?:-[a-z0-9]+)*-shelf)/([a-z0-9]+(?:-[a-z0-9]+)*)\.json')
PRIVATE = re.compile(r'(?i)(?:(?<![a-z])[a-z]:[/\\]|/users/|/home/|appdata|gh[pousr]_[a-z0-9]{20,}|sk-[a-z0-9]{20,})')
FIELDS = {'schema_version', 'shelf_id', 'source_id', 'candidate_id', 'work_title', 'language',
          'edition', 'translator', 'source_url', 'proposed_coverage', 'inspection_status',
          'inspection_notes', 'payload'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique_pairs(pairs):
    value = {}
    for key, item in pairs:
        require(key not in value, 'Duplicate JSON key')
        value[key] = item
    return value


def validate_proposal(root, name, bindings):
    match = PATTERN.fullmatch(name)
    require(match is not None, 'Only named shelf-proposal JSON is allowed outside release inventory')
    path = root / name
    require(not path.is_symlink() and path.resolve().is_relative_to(root.resolve()), 'Proposal path escapes checkout')
    require(path.is_file() and path.stat().st_size <= 65536, 'Proposal missing or larger than 64 KiB')
    raw = path.read_text(encoding='utf-8')
    require(not PRIVATE.search(raw), 'Proposal contains a private path or credential-like value')
    data = json.loads(raw, object_pairs_hook=unique_pairs)
    require(isinstance(data, dict) and set(data) == FIELDS, 'Unknown or missing proposal fields')
    require(type(data['schema_version']) is int and data['schema_version'] == 1, 'Unknown proposal schema')
    require(data['shelf_id'] == match[1] and data['candidate_id'] == match[2], 'Proposal identity differs from filename')
    require(bindings.get(data['shelf_id']) == data['source_id'], 'Unknown shelf or mismatched source authority')
    for field in FIELDS - {'schema_version', 'payload'}:
        require(isinstance(data[field], str) and data[field].strip(), 'Proposal text fields must be nonempty strings')
    url = urlsplit(data['source_url'])
    require(url.scheme in {'https', 'http'} and url.hostname and not url.username and not url.password,
            'Source URL must be a public HTTP(S) reference without credentials')
    require(url.hostname not in {'localhost', '127.0.0.1', '::1'} and not re.search(
        r'(?i)(token|password|signature|secret|api_key)=', url.query), 'Do not publish private or signed source URLs')
    require(data['proposed_coverage'] in {'complete-work', 'partial-work', 'selected-passages', 'fragmentary', 'unknown'},
            'Unknown proposed coverage')
    require(data['inspection_status'] in {'located', 'inspected'}, 'Proposals cannot claim admission or acceptance')
    payload = data['payload']
    if data['inspection_status'] == 'located':
        require(payload is None, 'Located-only sources must not claim payload inspection hashes')
    else:
        require(isinstance(payload, dict) and set(payload) == {'sha256', 'bytes', 'encoding'}, 'Inspected payload metadata missing')
        require(isinstance(payload['sha256'], str) and re.fullmatch('[0-9a-f]{64}', payload['sha256']), 'Invalid inspected hash')
        require(type(payload['bytes']) is int and payload['bytes'] > 0, 'Invalid inspected byte count')
        require(isinstance(payload['encoding'], str) and payload['encoding'].strip(), 'Missing encoding or not-applicable declaration')
    return data


def validate_proposals(root, release_files, tracked_names=None):
    root = Path(root).resolve()
    require(not any(n.startswith('contributions/') for n in release_files),
            'Proposals must remain outside the released collection inventory')
    mapping = root / 'collaboration/shelves.json'
    if not mapping.exists():
        if tracked_names is not None:
            require(set(tracked_names) == set(release_files) | {'release.json'}, 'Unknown tracked inventory; shelf proposal mapping missing')
        require(not (root / 'contributions').exists(), 'Shelf proposal mapping missing')
        return 0
    data = json.loads(mapping.read_text(encoding='utf-8'))
    pairs = data['shelves']
    bindings = {r['shelf_id']: r['source_id'] for r in pairs}
    require(len(bindings) == len(pairs), 'Duplicate shelf binding')
    registry = json.loads((root / 'library/library-registry.json').read_text(encoding='utf-8'))
    history = {s['source_id'] for s in registry['sources'] if s.get('section', 'history') == 'history'}
    require(set(bindings.values()) == history and len(bindings) == len(history), 'Shelf bindings differ from historical catalog')
    names = set(tracked_names) if tracked_names is not None else {
        p.relative_to(root).as_posix() for p in (root / 'contributions').rglob('*') if p.is_file()}
    extras = names - set(release_files) - {'release.json'} if tracked_names is not None else names
    for name in sorted(extras):
        validate_proposal(root, name, bindings)
    return len(extras)
