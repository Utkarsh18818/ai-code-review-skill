"""Compile and verify the bundled synthetic C++ cases on Linux."""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile

if __package__:
    from .cpp_benchmark import CORPUS, classify_execution, load_cases
else:
    from cpp_benchmark import CORPUS, classify_execution, load_cases


def execute(command, environment, timeout):
    return subprocess.run(command, env=environment, capture_output=True, text=True,
                          errors='replace', timeout=timeout, check=False)


def preserve_timeout(error, phase, log_path):
    def text(value):
        return value.decode("utf-8", errors="replace") if isinstance(value, bytes) else (value or "")

    log_path.write_text(text(error.stdout) + text(error.stderr), encoding="utf-8")
    return {"error": f"{type(error).__name__}: {error}", "failure_phase": phase,
            "timed_out": True, "timeout_seconds": error.timeout,
            "diagnostic_log": log_path.name}


def run(output, compiler):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    report = {'schema_version': 1, 'kind': 'sanitizer-fixture-verification', 'platform': platform.platform(),
              'source_revision': os.environ.get('GITHUB_SHA', 'unrecorded-local-run'),
              'started_at': datetime.now(timezone.utc).isoformat(),
              'compiler': compiler, 'cases': [], 'complete': False}
    try:
        if sys.platform != 'linux':
            raise ValueError('This runner requires Linux and working ASan/LSan/UBSan runtimes')
        compiler_path = shutil.which(compiler)
        if not compiler_path:
            raise ValueError('Clang C++ compiler unavailable; no cases verified')
        cases = load_cases()
        environment = {key: os.environ[key] for key in ('PATH', 'HOME', 'TMPDIR', 'LANG') if key in os.environ}
        environment.update(ASAN_OPTIONS='detect_leaks=1:halt_on_error=1:exitcode=86',
                           LSAN_OPTIONS='exitcode=86',
                           UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1:exitcode=86')
        version = execute([compiler_path, '--version'], environment, 10)
        if version.returncode:
            raise ValueError('Compiler version check failed')
        report['compiler_version'] = version.stdout.strip()
        report['sanitizer_environment'] = {k: environment[k] for k in ('ASAN_OPTIONS', 'LSAN_OPTIONS', 'UBSAN_OPTIONS')}
        with tempfile.TemporaryDirectory(prefix='cpp-review-') as temporary:
            for case in cases:
                binary = str(Path(temporary) / case['id'])
                command = [compiler_path, '-std=c++17', '-O0', '-g', '-fno-omit-frame-pointer',
                           '-fsanitize=address,undefined', '-fno-sanitize-recover=all',
                           '-fsanitize-address-use-after-scope', str(CORPUS / case['source']), '-o', binary]
                record = {'case_id': case['id'], 'source': case['source'],
                          'expected_defect': case['defective'], 'build_command': command,
                          'run_command': [binary], 'verified': False}
                phase = 'build'
                try:
                    built = execute(command, environment, 30)
                    record['build_exit'] = built.returncode
                    (output / f"{case['id']}-build.log").write_text(built.stdout + built.stderr, encoding='utf-8')
                    if built.returncode:
                        record['error'] = 'Compilation failed; program not executed'
                        print((built.stdout + built.stderr)[-6000:], file=sys.stderr)
                    else:
                        phase = 'run'
                        result = execute([binary], environment, 5)
                        combined = result.stdout + result.stderr
                        (output / f"{case['id']}-run.log").write_text(combined, encoding='utf-8')
                        record['run_exit'] = result.returncode
                        record['verified'] = classify_execution(case, result.returncode, combined)
                        if not record['verified']:
                            record['error'] = 'Observed behavior did not match expected diagnostic/clean execution'
                            print(f"{case['id']} unexpected exit {result.returncode}: {combined[-6000:]}", file=sys.stderr)
                except subprocess.TimeoutExpired as error:
                    record.update(preserve_timeout(error, phase, output / f"{case['id']}-{phase}.log"))
                except OSError as error:
                    record['error'] = f'{type(error).__name__}: {error}'
                    record['failure_phase'] = phase
                report['cases'].append(record)
        report['complete'] = len(report['cases']) == len(cases)
    except subprocess.TimeoutExpired as error:
        report.update(preserve_timeout(error, 'compiler-version', output / 'compiler-version.log'))
    except (OSError, ValueError, KeyError, TypeError) as error:
        report['error'] = f'{type(error).__name__}: {error}'
    passed = report['complete'] and all(case['verified'] for case in report['cases'])
    report['passed'] = passed
    (output / 'results.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    for case in report['cases']:
        print(f"{case['case_id']}: {'VERIFIED' if case['verified'] else 'FAILED'}")
    print(f"Fixture verification: {sum(c['verified'] for c in report['cases'])}/12; passed={passed}")
    if 'error' in report:
        print(report['error'], file=sys.stderr)
    return 0 if passed else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='benchmark-results')
    parser.add_argument('--compiler', default='clang++')
    options = parser.parse_args()
    sys.exit(run(options.output, options.compiler))
