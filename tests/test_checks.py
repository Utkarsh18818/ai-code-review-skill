import json
from pathlib import Path
import tempfile
import unittest

from scripts.check_sarif import check_directory
from scripts.validate_skill import validate


class SarifGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.report = {'version': '2.1.0', 'runs': [{
            'tool': {'driver': {'name': 'CodeQL'}},
            'invocations': [{'executionSuccessful': True}], 'results': []}]}

    def write(self):
        (self.root / 'result.sarif').write_text(json.dumps(self.report), encoding='utf-8')

    def test_clean_analysis_passes(self):
        self.write()
        self.assertEqual(check_directory(self.root), 1)

    def test_absent_evidence_blocks(self):
        with self.assertRaises(ValueError):
            check_directory(self.root)

    def test_findings_block_even_if_suppressed(self):
        self.report['runs'][0]['results'] = [{'ruleId': 'example', 'suppressions': [{'kind': 'inSource'}]}]
        self.write()
        with self.assertRaises(ValueError):
            check_directory(self.root)

    def test_failed_analysis_blocks(self):
        self.report['runs'][0]['invocations'][0]['executionSuccessful'] = False
        self.write()
        with self.assertRaises(ValueError):
            check_directory(self.root)

    def test_missing_results_blocks(self):
        del self.report['runs'][0]['results']
        self.write()
        with self.assertRaises(ValueError):
            check_directory(self.root)

    def test_empty_runs_blocks(self):
        self.report['runs'] = []
        self.write()
        with self.assertRaises(ValueError):
            check_directory(self.root)

    def test_malformed_json_blocks(self):
        (self.root / 'result.sarif').write_text('{', encoding='utf-8')
        with self.assertRaises(ValueError):
            check_directory(self.root)

    def test_unexpected_tool_blocks(self):
        self.report['runs'][0]['tool']['driver']['name'] = 'self-reported'
        self.write()
        with self.assertRaises(ValueError):
            check_directory(self.root)


class SkillValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.skill = self.root / 'SKILL.md'
        self.skill.write_text('---\nname: example\ndescription: Review example code.\n---\nReview instructions.\n', encoding='utf-8')

    def test_valid_skill(self):
        validate(self.root)

    def test_duplicate_metadata_blocks(self):
        text = self.skill.read_text(encoding='utf-8').replace('name: example', 'name: example\nname: other')
        self.skill.write_text(text, encoding='utf-8')
        with self.assertRaises(ValueError):
            validate(self.root)

    def test_broken_reference_blocks(self):
        with self.skill.open('a', encoding='utf-8') as stream:
            stream.write('[guide](missing.md)\n')
        with self.assertRaises(ValueError):
            validate(self.root)

    def test_reference_outside_package_blocks(self):
        with self.skill.open('a', encoding='utf-8') as stream:
            stream.write('[outside](../outside.md)\n')
        with self.assertRaises(ValueError):
            validate(self.root)


if __name__ == '__main__':
    unittest.main()
