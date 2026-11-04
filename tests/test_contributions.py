import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import contribution_checks as c


class ProposalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.name = 'contributions/twain-shelf/edition-one.json'
        self.path = self.root / self.name
        self.path.parent.mkdir(parents=True)
        self.data = {'schema_version': 1, 'shelf_id': 'twain-shelf', 'source_id': 'TWAIN',
                     'candidate_id': 'edition-one', 'work_title': 'A work', 'language': 'english',
                     'edition': 'Exact supplied edition', 'translator': 'not-applicable',
                     'source_url': 'https://example.org/edition', 'proposed_coverage': 'unknown',
                     'inspection_status': 'located', 'inspection_notes': 'Only the source page was inspected.', 'payload': None}

    def check(self):
        self.path.write_text(json.dumps(self.data), encoding='utf-8')
        return c.validate_proposal(self.root, self.name, {'twain-shelf': 'TWAIN'})

    def test_located_and_inspected(self):
        self.assertIsNone(self.check()['payload'])
        self.data.update(inspection_status='inspected', payload={'sha256': 'a'*64, 'bytes': 100, 'encoding': 'utf-8'})
        self.assertEqual(self.check()['payload']['bytes'], 100)

    def test_rejects_identity_scope_and_fabricated_states(self):
        original = copy.deepcopy(self.data)
        for field, value in [('source_id', 'OTHER'), ('candidate_id', 'wrong'), ('shelf_id', 'other-shelf'),
                             ('inspection_status', 'admitted'), ('proposed_coverage', 'author-complete'),
                             ('payload', {'sha256': 'a'*64}), ('source_url', 'file:///secret'),
                             ('source_url', 'https://user:pass@example.org/file'),
                             ('inspection_notes', 'C:/Users/Somebody/private/file.txt')]:
            with self.subTest(field=field, value=value):
                self.data = copy.deepcopy(original); self.data[field] = value
                with self.assertRaises(ValueError): self.check()

    def test_refuses_code_unknown_fields_and_oversized_records(self):
        self.path.write_text(json.dumps(self.data), encoding='utf-8')
        with self.assertRaises(ValueError): c.validate_proposal(self.root, 'contributions/twain-shelf/execute.py', {})
        self.data['unexpected'] = 'extra'
        with self.assertRaises(ValueError): self.check()
        self.path.write_text('x'*65537, encoding='utf-8')
        with self.assertRaises(ValueError): c.validate_proposal(self.root, self.name, {'twain-shelf':'TWAIN'})

    def test_duplicate_json_keys_fail(self):
        self.path.write_text('{"schema_version":1,"schema_version":1}', encoding='utf-8')
        with self.assertRaises(ValueError): c.validate_proposal(self.root, self.name, {'twain-shelf':'TWAIN'})

    def test_inventory_accepts_only_valid_unreleased_proposals(self):
        (self.root/'collaboration').mkdir(); (self.root/'library').mkdir()
        (self.root/'collaboration/shelves.json').write_text(json.dumps({'shelves':[{'shelf_id':'twain-shelf','source_id':'TWAIN'}]}))
        (self.root/'library/library-registry.json').write_text(json.dumps({'sources':[{'source_id':'TWAIN'}]}))
        self.check()
        self.assertEqual(c.validate_proposals(self.root, {'README.md'}, {'README.md','release.json',self.name}), 1)
        with self.assertRaises(ValueError): c.validate_proposals(self.root, {'README.md'}, {'README.md','release.json','other.py'})
        with self.assertRaises(ValueError): c.validate_proposals(self.root, {self.name}, {self.name,'release.json'})


if __name__ == '__main__':
    unittest.main()
