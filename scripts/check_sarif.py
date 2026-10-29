"""Fail closed when CodeQL reports findings or provides unusable evidence."""

import json
from pathlib import Path
import sys


def check_directory(directory):
    files = sorted(Path(directory).glob('*.sarif'))
    if not files:
        raise ValueError('No SARIF evidence found')
    findings = 0
    for file in files:
        data = json.loads(file.read_text(encoding='utf-8'))
        if data.get('version') != '2.1.0':
            raise ValueError('Unsupported SARIF version')
        runs = data.get('runs')
        if not isinstance(runs, list) or not runs:
            raise ValueError('Missing analysis runs')
        for run in runs:
            if run.get('tool', {}).get('driver', {}).get('name') != 'CodeQL':
                raise ValueError('Expected CodeQL analysis')
            invocations = run.get('invocations', [])
            if any(item.get('executionSuccessful') is False for item in invocations):
                raise ValueError('Analysis execution failed')
            results = run.get('results')
            if not isinstance(results, list):
                raise ValueError('Missing analysis results')
            findings += len(results)
    if findings:
        raise ValueError(f'CodeQL reported {findings} finding(s); review and fix before merging')
    return len(files)


def main():
    try:
        if len(sys.argv) != 2:
            raise ValueError('Usage: python3 scripts/check_sarif.py DIRECTORY')
        count = check_directory(sys.argv[1])
    except (ValueError, OSError, TypeError, AttributeError) as error:
        print(f'FAIL: {error}', file=sys.stderr)
        return 1
    print(f'PASS: {count} SARIF file(s), no reported findings')
    return 0


if __name__ == '__main__':
    sys.exit(main())
