# C++ memory-safety seed benchmark

Twelve small synthetic programs: six intentional defects and six corresponding safe controls, shuffled among neutral case IDs. They cover an early-return allocation leak, heap use-after-free, heap buffer overflow, double free, stack use after scope, and signed integer overflow. These are bounded local examples, not exploits against a live service.

## Verify fixture behavior with sanitizers

Run on Linux with Python 3.10+ and a Clang C++ toolchain with ASan/LSan/UBSan runtimes:

```sh
python3 scripts/run_cpp_benchmark.py --output benchmark-results
```

The runner compiles each case, captures commands/compiler version/platform, and executes each in a fresh process with a timeout. Vulnerable cases must exit nonzero with the expected sanitizer diagnostic. Safe controls must exit zero with no sanitizer error. Missing tools, failed compilation, crashes without the expected diagnosis, or timeouts fail verification. Logs and machine-readable results are saved even when a case fails. Compilation and execution timeouts preserve captured stdout/stderr in the phase-specific log; JSON records the failed phase, timeout duration, and log filename. Compiler-version timeouts preserve the same evidence in a toolchain log. Binaries live in a temporary directory and are removed on exit; reproduction commands need a fresh build.

The required CI gate runs this suite on Ubuntu. Intentionally vulnerable fixtures are only for testing the reviewer and sanitizer setup. CodeQL continues to scan the Python tooling and Actions workflow; this suite is the native runtime check. No sanitizer run proves the absence of defects outside executed paths.

## Evaluate a reviewer separately

Sanitizer fixture verification is **not** an AI detection score. To evaluate the skill:

1. Give a reviewer the skill and only the neutral `cases/` sources. Do not give it `manifest.json`, this README's answer categories, sanitizer logs, paired-case information, or prior conclusions. Use a fresh session and record model/version, prompt, date, tool access, skill revision, and settings.
2. Ask it to review each source independently, using the skill, and return one record per case in the format below. Archive the complete unedited reviews as well as the records. Do not substitute a hand-written answer key for actual model output.
3. Run the scorer against the original manifest; have a human verify every claimed location, category, and evidence trace. The scorer validates structure and category agreement, not whether the model's reasoning is sound.
4. Repeat with held-out, realistic cases before making accuracy claims. This tiny public seed set is susceptible to memorization and does not test authorization, races, descriptor leaks, or production integration.

```json
{
  "reviewer": {"model": "record actual model", "skill_revision": "record actual commit", "prompt": "record exact prompt", "date": "record run date"},
  "predictions": [
    {"case_id": "n01", "verdict": "unassessed", "reason": "example format only"}
  ]
}
```

Use `issue`, `clean`, or `unassessed` as the verdict. `issue` requires `category`, a 1-based `line` in the source, and nonempty `evidence`; `clean` requires nonempty `evidence` describing what was checked; `unassessed` requires `reason`. Categories are `leak`, `heap-use-after-free`, `heap-buffer-overflow`, `double-free`, `stack-use-after-scope`, and `signed-integer-overflow`. Complete all twelve records; the abbreviated example is not a completed evaluation.

```sh
python3 scripts/score_cpp_review.py actual-review.json
```

The score reports confirmed-category true positives, false positives, missed defects, true negatives, precision, recall, and false-positive rate. A wrong category on a defective case counts as both an unsupported finding and a missed expected defect. Missing/duplicate/unknown records or invalid locations fail scoring. Any unassessed case marks the evaluation incomplete and withholds rates. Nonzero exit means incomplete/invalid evaluation, not a model accuracy threshold. Report the counts with every percentage; keep evidence-quality adjudication separate.

## Current evidence

This version adds executable fixture verification and a reviewer-scoring harness. No independent AI-review accuracy result is claimed. CI artifacts establish sanitizer behavior only; publish actual review runs and human adjudication before advertising detection performance.
