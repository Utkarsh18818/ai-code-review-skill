"""Score declared review categories; evidence still needs human adjudication."""

import json
from pathlib import Path
import sys

if __package__:
    from .cpp_benchmark import CORPUS, load_cases
else:
    from cpp_benchmark import CORPUS, load_cases


def score(document, root=CORPUS):
    cases = {case['id']: case for case in load_cases(root)}
    metadata = document.get('reviewer', {})
    for key in ('model', 'skill_revision', 'prompt', 'date'):
        if not isinstance(metadata.get(key), str) or not metadata[key].strip():
            raise ValueError(f'Missing reviewer metadata: {key}')
    predictions = document.get('predictions')
    if not isinstance(predictions, list):
        raise ValueError('Missing predictions')
    seen = set()
    counts = {'true_positives': 0, 'false_positives': 0, 'false_negatives': 0, 'true_negatives': 0}
    unassessed = []
    for prediction in predictions:
        case_id = prediction['case_id']
        if case_id not in cases or case_id in seen:
            raise ValueError('Unknown or duplicate case ID')
        seen.add(case_id)
        case = cases[case_id]
        verdict = prediction['verdict']
        if verdict == 'unassessed':
            if not isinstance(prediction.get('reason'), str) or not prediction['reason'].strip():
                raise ValueError('Unassessed cases need a reason')
            unassessed.append(case_id)
            continue
        if verdict not in ('issue', 'clean'):
            raise ValueError('Unsupported verdict')
        if not isinstance(prediction.get('evidence'), str) or not prediction['evidence'].strip():
            raise ValueError('Assessed cases need evidence')
        if verdict == 'issue':
            line = prediction.get('line')
            line_count = len((Path(root) / case['source']).read_text(encoding='utf-8').splitlines())
            if type(line) is not int or not 1 <= line <= line_count:
                raise ValueError('Finding line is outside source')
            if not isinstance(prediction.get('category'), str) or not prediction['category'].strip():
                raise ValueError('Finding needs a category')
        matched = verdict == 'issue' and prediction['category'] == case['category']
        if case['defective']:
            counts['true_positives' if matched else 'false_negatives'] += 1
            if verdict == 'issue' and not matched:
                counts['false_positives'] += 1
        else:
            counts['false_positives' if verdict == 'issue' else 'true_negatives'] += 1
    if seen != set(cases):
        raise ValueError('Every case must have a record; omissions are not clean verdicts')
    result = {'kind': 'declared-category-review-score', 'reviewer': metadata, 'counts': counts,
              'complete': not unassessed, 'unassessed': unassessed,
              'evidence_quality': 'not automatically adjudicated'}
    if not unassessed:
        tp, fp, fn, tn = (counts[key] for key in ('true_positives', 'false_positives', 'false_negatives', 'true_negatives'))
        result.update(precision=tp / (tp + fp) if tp + fp else None,
                      recall=tp / (tp + fn) if tp + fn else None,
                      false_positive_rate=sum(p['verdict'] == 'issue' and not cases[p['case_id']]['defective'] for p in predictions) / 6)
    return result


if __name__ == '__main__':
    try:
        if len(sys.argv) != 2:
            raise ValueError('Usage: python3 scripts/score_cpp_review.py ACTUAL_REVIEW.json')
        result = score(json.loads(Path(sys.argv[1]).read_text(encoding='utf-8')))
        print(json.dumps(result, indent=2))
        sys.exit(0 if result['complete'] else 1)
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
        print(f'Invalid evaluation: {error}', file=sys.stderr)
        sys.exit(1)
