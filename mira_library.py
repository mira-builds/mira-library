"""Browse metadata and retrieve hash-verified local passages without network access."""
import argparse
import json
import sys

import catalog
import passages


def main(argv=None):
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('list', 'show', 'verify', 'read'):
        p = sub.add_parser(name)
        p.add_argument('--json', action='store_true')
        if name in {'verify', 'read'}:
            p.add_argument('--text-root')
        if name in {'list', 'verify'}:
            p.add_argument('--source')
        if name == 'list':
            p.add_argument('--query', default='')
            p.add_argument('--era')
        if name in {'show', 'read'}:
            p.add_argument('source_id')
        if name == 'verify':
            p.add_argument('--body')
        if name == 'read':
            p.add_argument('body_id')
            choice = p.add_mutually_exclusive_group(required=True)
            choice.add_argument('--query')
            choice.add_argument('--locator-json')
    args = parser.parse_args(argv)
    try:
        registry = catalog.load_registry()
        if args.command == 'list':
            sources = [catalog.select(registry, args.source)] if args.source else registry['sources']
            result = {'status': 'ok', 'sources': [
                {'source_id': s['source_id'], 'title': s['title'], 'author': s.get('author', ''),
                 'era': s.get('subject_era'), 'bodies': len(catalog.all_text_bodies(s))}
                for s in sources if (not args.era or s.get('subject_era') == args.era)
                and args.query.casefold() in json.dumps(s, ensure_ascii=False).casefold()]}
        elif args.command == 'show':
            result = {'status': 'ok', 'source': catalog.select(registry, args.source_id)}
        elif args.command == 'verify':
            result = catalog.verify(registry, args.text_root, args.source, args.body)
        else:
            passages.TEXT_ROOT = catalog.resolve_root(args.text_root)
            result = passages.read(args.source_id, args.body_id, query=args.query,
                                   locator=json.loads(args.locator_json) if args.locator_json else None)
    except (catalog.LibraryError, passages.PassageError, OSError, ValueError) as error:
        result = {'status': 'failed', 'error_category': getattr(error, 'category', 'invalid-input'), 'error': str(error)}
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif 'sources' in result:
        for s in result['sources']:
            print(f"{s['source_id']} | {s['author']} | {s['title']} | {s['bodies']} bodies")
    elif 'passages' in result:
        print(result['status'])
        for p in result['passages']:
            print(f"\n{p['edition']} | {p['language']} | {p.get('translator') or ''}\n{p['text']}\nLocator: {json.dumps(p['locator'])}")
    elif 'counts' in result:
        print(result['status'] + ': ' + ', '.join(f'{k}={v}' for k, v in result['counts'].items()))
        for row in result['results']:
            if row['status'] != 'verified':
                print(f"{row['source_id']} {row.get('body_id', '')}: {row['status']}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result['status'] == 'failed' else 0


if __name__ == '__main__':
    sys.exit(main())
