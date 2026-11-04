import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import checks


class CatalogCheckTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'library').mkdir()
        self.registry = {'schema_version': 1, 'sources': [{'source_id': 'S1', 'title': 'A work', 'text_bodies': [
            {'body_id': 'B1', 'work_title': 'A work', 'status': 'available', 'text_location': 'library-text://work.txt',
             'text_sha256': 'a' * 64, 'text_bytes': 10, 'text_encoding': 'utf-8'}]}]}
        (self.root / 'README.md').write_text('[Catalog](library/library-registry.json)\n', encoding='utf-8')
        self.write()

    def write(self):
        (self.root / 'library/library-registry.json').write_text(json.dumps(self.registry), encoding='utf-8')
        self.release = {'format': 'mira-library-public-v1', 'sources': 1, 'bodies': 1,
                        'files': {name: hashlib.sha256((self.root / name).read_bytes()).hexdigest()
                                  for name in ('README.md', 'library/library-registry.json')}}
        self.save_release()

    def save_release(self):
        (self.root / 'release.json').write_text(json.dumps(self.release), encoding='utf-8')

    def test_valid_without_archive(self):
        self.assertFalse(checks.validate(self.root)['archive_required'])

    def test_metadata_only_source(self):
        self.registry['sources'][0]['text_bodies'] = []
        self.write()
        self.release['bodies'] = 0
        self.save_release()
        self.assertEqual(checks.validate(self.root)['bodies'], 0)

    def test_checksum_failure(self):
        (self.root / 'README.md').write_text('changed')
        with self.assertRaisesRegex(checks.CheckError, 'checksum mismatch'):
            checks.validate(self.root)

    def test_missing_file(self):
        (self.root / 'README.md').unlink()
        with self.assertRaisesRegex(checks.CheckError, 'Missing published'):
            checks.validate(self.root)

    def test_counts(self):
        self.release['sources'] = 2
        self.save_release()
        with self.assertRaisesRegex(checks.CheckError, 'source count'):
            checks.validate(self.root)

    def test_duplicate_sources(self):
        self.registry['sources'].append(copy.deepcopy(self.registry['sources'][0]))
        self.write()
        with self.assertRaisesRegex(checks.CheckError, 'source identity'):
            checks.validate(self.root)

    def test_duplicate_bodies(self):
        bodies = self.registry['sources'][0]['text_bodies']
        bodies.append(copy.deepcopy(bodies[0]))
        self.write()
        with self.assertRaisesRegex(checks.CheckError, 'body identity'):
            checks.validate(self.root)

    def test_bad_body_metadata(self):
        original = copy.deepcopy(self.registry)
        for field, value in [('text_sha256', 'bad'), ('text_bytes', True), ('status', 'unknown'),
                             ('text_location', 'library-text://../outside'), ('text_location', '/outside')]:
            with self.subTest(field=field, value=value):
                self.registry = copy.deepcopy(original)
                self.registry['sources'][0]['text_bodies'][0][field] = value
                self.write()
                with self.assertRaises(checks.CheckError):
                    checks.validate(self.root)

    def test_unsafe_inventory_path(self):
        self.release['files']['../outside'] = 'a' * 64
        self.save_release()
        with self.assertRaisesRegex(checks.CheckError, 'Unsafe relative path'):
            checks.validate(self.root)

    def test_broken_link(self):
        (self.root / 'README.md').write_text('[Missing](absent.md)')
        self.write()
        with self.assertRaisesRegex(checks.CheckError, 'Broken local link'):
            checks.validate(self.root)

    def test_tracked_inventory(self):
        names = b'README.md\0library/library-registry.json\0release.json\0'
        with patch.object(subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, stdout=names)):
            self.assertTrue(checks.validate(self.root, tracked=True)['tracked_inventory_checked'])
        with patch.object(subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, stdout=names+b'extra.txt\0')):
            with self.assertRaisesRegex(checks.CheckError, 'tracked inventory'):
                checks.validate(self.root, tracked=True)


if __name__ == '__main__':
    unittest.main()
