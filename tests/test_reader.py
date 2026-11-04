import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import catalog
import passages


class ReaderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.repo = self.base / 'checkout'
        (self.repo / 'library').mkdir(parents=True)
        self.archive = self.base / 'texts'
        self.archive.mkdir()
        self.data = b'First sentence. Sovereignty needs careful interpretation.\n\nAnother paragraph.'
        self.body = {'body_id': 'BODY-1', 'work_title': 'Synthetic work', 'text_location': 'library-text://work.txt',
                     'text_sha256': hashlib.sha256(self.data).hexdigest(), 'text_bytes': len(self.data),
                     'text_encoding': 'utf-8', 'status': 'verified', 'edition_label': 'Synthetic edition',
                     'translator': 'Example translator', 'language': 'english'}
        self.registry = {'sources': [{'source_id': 'SOURCE-1', 'title': 'Synthetic work', 'text_bodies': [self.body]}]}
        self.save()
        (self.archive / 'work.txt').write_bytes(self.data)
        self.previous_root = passages.TEXT_ROOT
        passages.TEXT_ROOT = self.archive
        self.addCleanup(setattr, passages, 'TEXT_ROOT', self.previous_root)

    def save(self):
        (self.repo / 'library/library-registry.json').write_text(json.dumps(self.registry), encoding='utf-8')

    def test_browse_without_archive(self):
        self.assertEqual(catalog.select(self.registry, 'SOURCE-1')['title'], 'Synthetic work')

    def test_cli_utf8_without_core_environment(self):
        for name in ('catalog.py', 'passages.py', 'mira_library.py'):
            shutil.copyfile(Path(__file__).resolve().parents[1] / name, self.repo / name)
        self.registry['sources'][0]['title'] = 'Édition — 文'
        self.save()
        env = {k: v for k, v in os.environ.items() if not k.startswith('MIRA_') and k not in {'PYTHONPATH', 'PYTHONHOME'}}
        process = subprocess.run([sys.executable, '-E', '-s', '-B', str(self.repo / 'mira_library.py'), 'list', '--json'],
                                 cwd=self.repo, env=env, capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(json.loads(process.stdout)['sources'][0]['title'], 'Édition — 文')

    def test_configuration_and_precedence(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(catalog.LibraryError, 'Supply'):
                catalog.resolve_root()
        with patch.dict(os.environ, {'MIRA_LIBRARY_TEXT_ROOT': str(self.base / 'absent')}):
            self.assertEqual(catalog.resolve_root(self.archive), self.archive.resolve())

    def test_verified_read_and_locator_replay(self):
        result = passages.read('SOURCE-1', 'BODY-1', query='sovereignty', repo=self.repo)
        p = result['passages'][0]
        self.assertEqual(p['text'], 'Sovereignty needs careful interpretation.')
        self.assertEqual(p['edition'], 'Synthetic edition')
        self.assertEqual(p['ref'], 'library-text://work.txt')
        replay = passages.read('SOURCE-1', 'BODY-1', locator=p['locator'], repo=self.repo)
        self.assertEqual(replay['passages'][0], p)

    def test_relocated_archive(self):
        moved = self.base / 'relocated'
        shutil.move(self.archive, moved)
        passages.TEXT_ROOT = moved
        self.assertEqual(passages.read('SOURCE-1', 'BODY-1', query='sovereignty', repo=self.repo)['status'], 'ok')

    def test_missing_and_corrupt(self):
        path = self.archive / 'work.txt'
        path.unlink()
        with self.assertRaises(catalog.LibraryError) as caught:
            catalog.verified_bytes(self.body, self.archive)
        self.assertEqual(caught.exception.category, 'missing')
        path.write_bytes(b'changed')
        with self.assertRaises(catalog.LibraryError) as caught:
            catalog.verified_bytes(self.body, self.archive)
        self.assertEqual(caught.exception.category, 'hash-mismatch')

    def test_byte_length_checked(self):
        self.body['text_bytes'] += 1
        with self.assertRaisesRegex(catalog.LibraryError, 'digest or size'):
            catalog.verified_bytes(self.body, self.archive)

    def test_unavailable_separate_from_missing(self):
        self.registry['sources'].append({'source_id': 'SOURCE-2', 'text_bodies': []})
        result = catalog.verify(self.registry, self.archive)
        self.assertEqual(result['counts'], {'unavailable': 1, 'verified': 1})
        self.body['status'] = 'needs-review'
        self.assertEqual(catalog.verify(self.registry, self.archive)['counts'], {'unavailable': 2})

    def test_unsafe_locations(self):
        for suffix in ('../escape', '/absolute', 'folder//file', 'folder/./file', 'folder\\file', 'disk:file'):
            with self.subTest(suffix=suffix):
                self.body['text_location'] = 'library-text://' + suffix
                with self.assertRaises(catalog.LibraryError):
                    catalog.verified_bytes(self.body, self.archive)

    def test_archive_inside_checkout(self):
        with self.assertRaises(catalog.LibraryError):
            catalog.resolve_root(self.repo / 'library', self.repo)

    def test_symlink_escape(self):
        link = self.archive / 'link.txt'
        try:
            link.symlink_to(self.repo / 'library/library-registry.json')
        except OSError:
            self.skipTest('Host does not permit symlink creation')
        self.body['text_location'] = 'library-text://link.txt'
        with self.assertRaisesRegex(catalog.LibraryError, 'escapes'):
            catalog.verified_bytes(self.body, self.archive, self.repo)

    def test_unsupported_encoding(self):
        self.body['text_encoding'] = 'not-an-encoding'
        self.save()
        with self.assertRaises(passages.PassageError) as caught:
            passages.read('SOURCE-1', 'BODY-1', query='sovereignty', repo=self.repo)
        self.assertEqual(caught.exception.category, 'unsupported')

    def test_resolved_escape_rejected_without_symlink_privilege(self):
        original_resolve = Path.resolve
        # Windows temporary roots may use short names that resolve to long names.
        escaping = (self.archive / 'work.txt').resolve()
        def resolve(path, *args, **kwargs):
            resolved = original_resolve(path, *args, **kwargs)
            if resolved == escaping:
                return original_resolve(self.base / 'outside.txt')
            return resolved
        with patch.object(Path, 'resolve', resolve), self.assertRaisesRegex(catalog.LibraryError, 'escapes'):
            catalog.verified_bytes(self.body, self.archive, self.repo)

    def test_locator_identity_and_digest(self):
        p = passages.read('SOURCE-1', 'BODY-1', query='sovereignty', repo=self.repo)['passages'][0]
        for key in ('source_id', 'body_id', 'source_sha256', 'excerpt_sha256'):
            loc = dict(p['locator'], **{key: 'wrong'})
            with self.subTest(key=key), self.assertRaises(passages.PassageError):
                passages.read('SOURCE-1', 'BODY-1', locator=loc, repo=self.repo)

    def test_unknown_and_duplicate_identities(self):
        with self.assertRaises(catalog.LibraryError):
            catalog.select(self.registry, 'missing')
        self.registry['sources'].append(self.registry['sources'][0])
        with self.assertRaises(catalog.LibraryError):
            catalog.select(self.registry, 'SOURCE-1')

    def test_tei_locator(self):
        data = b'<TEI><text><body><div><head>Book One</head><p n="1">Sovereignty is discussed here.</p></div></body></text></TEI>'
        (self.archive / 'work.xml').write_bytes(data)
        self.body.update(text_location='library-text://work.xml', text_bytes=len(data), text_sha256=hashlib.sha256(data).hexdigest())
        self.save()
        p = passages.read('SOURCE-1', 'BODY-1', query='sovereignty', repo=self.repo)['passages'][0]
        self.assertEqual(p['structure']['section'], 'Book One')
        self.assertEqual(p['structure']['n'], '1')


if __name__ == '__main__':
    unittest.main()
