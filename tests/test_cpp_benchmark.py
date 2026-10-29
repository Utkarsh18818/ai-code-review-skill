import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.cpp_benchmark import classify_execution, load_cases
from scripts.run_cpp_benchmark import run
from scripts.score_cpp_review import score


class FixtureTests(unittest.TestCase):
    def test_corpus_has_six_pairs(self):
        cases = load_cases()
        self.assertEqual(len(cases), 12)
        self.assertEqual(sum(case['defective'] for case in cases), 6)

    def test_crash_without_expected_diagnostic_is_not_detection(self):
        case = {'defective': True, 'diagnostic': 'heap-use-after-free'}
        self.assertFalse(classify_execution(case, -11, 'Segmentation fault'))
        self.assertFalse(classify_execution(case, 0, 'heap-use-after-free'))
        self.assertTrue(classify_execution(case, 86, 'AddressSanitizer: heap-use-after-free'))

    def test_safe_control_requires_clean_success(self):
        case = {'defective': False, 'diagnostic': ''}
        self.assertTrue(classify_execution(case, 0, ''))
        self.assertFalse(classify_execution(case, 1, ''))
        self.assertFalse(classify_execution(case, 0, 'runtime error: overflow'))

    def test_unsupported_platform_fails_with_report(self):
        with tempfile.TemporaryDirectory() as directory, patch('scripts.run_cpp_benchmark.sys.platform', 'win32'):
            self.assertEqual(run(directory, 'clang++'), 1)
            report = json.loads((Path(directory) / 'results.json').read_text(encoding='utf-8'))
            self.assertFalse(report['passed'])
            self.assertFalse(report['complete'])


class ReviewScoringTests(unittest.TestCase):
    def setUp(self):
        # Synthetic scorer unit input, not model output or an accuracy result.
        self.document = {
            'reviewer': {'model': 'unit-test', 'skill_revision': 'unit-test', 'prompt': 'unit-test', 'date': 'unit-test'},
            'predictions': [{'case_id': case['id'], 'verdict': 'issue' if case['defective'] else 'clean',
                             'category': case['category'], 'line': 1, 'evidence': 'Synthetic scorer test'}
                            for case in load_cases()]}

    def test_matching_categories_and_safe_controls(self):
        result = score(self.document)
        self.assertEqual(result['counts'], {'true_positives': 6, 'false_positives': 0,
                                           'false_negatives': 0, 'true_negatives': 6})

    def test_all_clean_reports_six_misses(self):
        for prediction in self.document['predictions']:
            prediction['verdict'] = 'clean'
        result = score(self.document)
        self.assertEqual(result['counts']['false_negatives'], 6)
        self.assertEqual(result['recall'], 0)
        self.assertIsNone(result['precision'])

    def test_wrong_category_counts_unsupported_and_missed(self):
        self.document['predictions'][0]['category'] = 'wrong-category'
        result = score(self.document)
        self.assertEqual(result['counts']['false_positives'], 1)
        self.assertEqual(result['counts']['false_negatives'], 1)

    def test_safe_case_finding_counts_false_alarm(self):
        self.document['predictions'][1]['verdict'] = 'issue'
        result = score(self.document)
        self.assertEqual(result['counts']['false_positives'], 1)
        self.assertAlmostEqual(result['false_positive_rate'], 1 / 6)

    def test_unassessed_withholds_rates(self):
        self.document['predictions'][0] = {'case_id': 'n01', 'verdict': 'unassessed', 'reason': 'Tool unavailable'}
        result = score(self.document)
        self.assertFalse(result['complete'])
        self.assertNotIn('recall', result)
        self.assertNotIn('precision', result)

    def test_omission_rejected(self):
        self.document['predictions'].pop()
        with self.assertRaises(ValueError):
            score(self.document)

    def test_duplicate_rejected(self):
        self.document['predictions'].append(copy.deepcopy(self.document['predictions'][0]))
        with self.assertRaises(ValueError):
            score(self.document)

    def test_out_of_range_line_rejected(self):
        self.document['predictions'][0]['line'] = 9999
        with self.assertRaises(ValueError):
            score(self.document)

    def test_empty_evidence_rejected(self):
        self.document['predictions'][0]['evidence'] = ''
        with self.assertRaises(ValueError):
            score(self.document)


if __name__ == '__main__':
    unittest.main()
