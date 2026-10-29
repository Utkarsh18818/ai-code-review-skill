"""Shared seed-corpus loading and result classification."""

import json
from pathlib import Path
import re


CATEGORIES = {'leak', 'heap-use-after-free', 'heap-buffer-overflow', 'double-free',
              'stack-use-after-scope', 'signed-integer-overflow'}
CORPUS = Path(__file__).resolve().parents[1] / 'benchmarks' / 'cpp'


def load_cases(root=CORPUS):
    root = Path(root).resolve()
    data = json.loads((root / 'manifest.json').read_text(encoding='utf-8'))
    if data.get('schema_version') != 1:
        raise ValueError('Unsupported corpus schema')
    cases = data.get('cases')
    if not isinstance(cases, list) or len(cases) != 12:
        raise ValueError('Expected all twelve seed cases')
    ids = set()
    for case in cases:
        case_id = case['id']
        if not re.fullmatch(r'n[0-9]{2}', case_id) or case_id in ids:
            raise ValueError('Invalid or duplicate case ID')
        ids.add(case_id)
        if case['category'] not in CATEGORIES or type(case['defective']) is not bool:
            raise ValueError('Invalid ground truth')
        if case['source'] != f'cases/{case_id}.cpp':
            raise ValueError('Unexpected source path')
        source = (root / case['source']).resolve()
        if not source.is_relative_to(root) or not source.is_file():
            raise ValueError('Source missing or outside corpus')
        diagnostic = case['diagnostic']
        if not isinstance(diagnostic, str) or bool(diagnostic) != case['defective']:
            raise ValueError('Expected defect diagnostic or empty safe diagnostic')
    if {p.stem for p in (root / 'cases').glob('*.cpp')} != ids:
        raise ValueError('Untracked or missing corpus sources')
    for category in CATEGORIES:
        pair = [c['defective'] for c in cases if c['category'] == category]
        if sorted(pair) != [False, True]:
            raise ValueError('Each category needs one defect and one safe control')
    return cases


def classify_execution(case, returncode, output):
    if case['defective']:
        return returncode != 0 and case['diagnostic'] in output
    markers = ('AddressSanitizer', 'LeakSanitizer', 'UndefinedBehaviorSanitizer', 'runtime error:')
    return returncode == 0 and not any(marker in output for marker in markers)
