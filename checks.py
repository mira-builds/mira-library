"""Validate published metadata without access to any archive body or network."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import posixpath
import re
import subprocess
import sys


class CheckError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise CheckError(message)


def relative_path(value):
    require(isinstance(value, str) and bool(value), 'Empty or invalid relative path')
    require('\\' not in value and ':' not in value and
            all(p not in {'', '.', '..', '.git'} for p in value.split('/')), 'Unsafe relative path: ' + value)
    return value


def validate(root, tracked=False):
    root = Path(root).resolve()
    release = json.loads((root / 'release.json').read_text(encoding='utf-8'))
    require(release.get('format') == 'mira-library-public-v1', 'Unknown release format')
    files = release.get('files')
    require(isinstance(files, dict) and files, 'Release file inventory is missing')
    require('release.json' not in files, 'Release inventory must exclude itself')
    for name, expected in files.items():
        path = root / relative_path(name)
        require(path.resolve().is_relative_to(root), 'File escapes checkout: ' + name)
        require(path.is_file(), 'Missing published file: ' + name)
        require(isinstance(expected, str) and re.fullmatch('[0-9a-f]{64}', expected), 'Invalid file digest: ' + name)
        require(hashlib.sha256(path.read_bytes()).hexdigest() == expected, 'Published checksum mismatch: ' + name)
    if tracked:
        result = subprocess.run(['git', '-C', str(root), 'ls-files', '-z'], capture_output=True, check=True)
        names = set(result.stdout.decode('utf-8').rstrip('\0').split('\0'))
        require(names == set(files) | {'release.json'}, 'Git tracked inventory differs from release inventory')
    registry = json.loads((root / 'library/library-registry.json').read_text(encoding='utf-8'))
    require(registry.get('schema_version') == 1, 'Unknown catalog schema')
    sources = registry.get('sources')
    require(isinstance(sources, list), 'Catalog sources must be a list')
    source_ids, body_ids = set(), set()
    for source in sources:
        sid = source.get('source_id')
        require(isinstance(sid, str) and sid and sid not in source_ids, 'Missing or duplicate source identity')
        require(isinstance(source.get('title'), str) and source['title'].strip(), 'Missing source title: ' + sid)
        source_ids.add(sid)
        bodies = source.get('text_bodies', [])
        require(isinstance(bodies, list), 'Body list is invalid: ' + sid)
        for body in bodies:
            bid = body.get('body_id')
            require(isinstance(bid, str) and bid and bid not in body_ids, 'Missing or duplicate body identity')
            body_ids.add(bid)
            require(body.get('status') in {'available', 'verified', 'needs-review'}, 'Unknown body status: ' + bid)
            require(isinstance(body.get('work_title'), str) and body['work_title'].strip(), 'Missing body title: ' + bid)
            uri = body.get('text_location', '')
            require(isinstance(uri, str) and uri.startswith('library-text://'), 'Nonportable body location: ' + bid)
            relative_path(uri[len('library-text://'):])
            require(isinstance(body.get('text_sha256'), str) and re.fullmatch('[0-9a-f]{64}', body['text_sha256']), 'Invalid body digest: ' + bid)
            require(type(body.get('text_bytes')) is int and body['text_bytes'] > 0, 'Invalid body size: ' + bid)
            require(isinstance(body.get('text_encoding'), str) and body['text_encoding'], 'Missing encoding: ' + bid)
    require(release.get('sources') == len(source_ids), 'Release source count mismatch')
    require(release.get('bodies') == len(body_ids), 'Release body count mismatch')
    for name in files:
        if not name.endswith('.md'):
            continue
        text = (root / name).read_text(encoding='utf-8')
        for link in re.findall(r'\]\(([^)]+)\)', text):
            target = link.split('#', 1)[0]
            if not target or '://' in target or target.startswith('mailto:'):
                continue
            target = posixpath.normpath(posixpath.join(str(PurePosixPath(name).parent), target))
            require(target in files or target == 'release.json', 'Broken local link: ' + name + ' -> ' + target)
    return {'status': 'passed', 'sources': len(source_ids), 'bodies': len(body_ids),
            'files': len(files) + 1, 'tracked_inventory_checked': tracked, 'archive_required': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tracked', action='store_true', help='Also compare Git tracked files with the release inventory')
    args = parser.parse_args()
    try:
        result = validate(Path(__file__).resolve().parent, args.tracked)
    except (CheckError, OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        print(json.dumps({'status': 'failed', 'error': str(error)}))
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
