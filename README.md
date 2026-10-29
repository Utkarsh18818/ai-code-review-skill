# AI Code Review

A reusable agent skill for reviewing AI-generated and human-written code for security vulnerabilities, memory/resource leaks, correctness, and weakened verification.

## Install locally

Copy this folder into your repository as `.agents/skills/ai-code-review/`, keeping `SKILL.md` and `references/` together. Codex discovers repository skills there. If it does not appear, restart Codex.

## Use

```text
Use $ai-code-review to review the changes between main and my current branch.
Prioritize security vulnerabilities, memory/resource leaks, and data integrity.
Report verified findings with locations, evidence, and suggested fixes.
```

```text
Use $ai-code-review to audit the ownership and error paths in src/parser.cpp.
Do not modify the code. State which checks you could not run.
```

The skill adapts to the repository's languages and tools. It reports confirmed findings separately from verification gaps and returns an advisory disposition: Changes required, Incomplete, or No blocking findings identified. It does not automatically fix code or post reviews.

## Coverage

- Authentication, authorization, injection, file/network boundaries, secrets, and cryptography.
- Memory safety, ownership, error-path cleanup, retained resources, concurrency, and exhaustion.
- Dependency risks, production correctness, test quality, and attempts to weaken verification.

No external service or API key is required by the instructions themselves. Running repository tests/scanners may require stack-specific tools. Live advisory lookups require network access. Missing tools are reported as coverage gaps.

## Enforcement limits

This is a review skill, not an unbypassable security system. It cannot guarantee finding every vulnerability. Installing it in another project does not configure that project's CI or branch protections. See [enforcement guidance](references/enforcement.md).

This source repository includes a `Review Gate` workflow: package validation, unit tests, CodeQL security-extended analysis for Python and GitHub Actions, and a C++ sanitizer fixture suite. `Required Review Gate` succeeds only when all prerequisites succeed. Each scanner job also rejects reported findings and missing/malformed SARIF evidence. These checks cover this repository, not code in projects that install the skill. See [security policy](SECURITY.md).

Run local checks with Python 3.10 or newer:

```text
python scripts/validate_skill.py
python -m unittest discover -s tests -v
```

Branch protection and independent human approval must be configured on GitHub; workflow files alone do not enforce them. An owner cannot approve their own PR and will need a second eligible collaborator to approve owner-authored changes. Administrators with permission to edit protection settings remain a trust boundary.

## Publish and contribute

Publish this folder in a public GitHub repository, preserving LICENSE. Include example prompts and supported-tool notes in your listing. Others can install from the repository with Codex's skill installer. For plugin-directory discovery, package it as a plugin and follow the current submission process.

Contributions should include the observed review failure, a small synthetic reproduction or example, expected behavior, and any relevant environment/tool versions. Do not submit credentials, private source code, or weaponized exploits. Prefer focused improvements over instructions that force irrelevant checks on every project.

The validation utilities have unit tests, including checks that missing evidence and scanner findings block the gate. The review skill itself has not been benchmarked against a representative vulnerable-code corpus. Before relying on it, evaluate known-vulnerable examples and safe controls for your stack, including prompt injection, cleanup failures, authorization bypasses, and missing scanner coverage.

## C++ evidence and benchmarking

For C++ reviews, the skill adds [ownership/lifetime review guidance](references/cpp-review.md), reproducible sanitizer evidence, a detailed finding format, and behavior-based regression-test guidance.

The [C++ seed benchmark](benchmarks/cpp/README.md) provides twelve shuffled sources: six defects and six safe controls. It covers allocation leaks, use-after-free, buffer overflow, double free, stack lifetime, and integer overflow. A Linux runner verifies the expected ASan/LSan/UBSan behavior and preserves logs, build commands, toolchain details, and JSON outcomes as CI artifacts. Missing tools and unexpected behavior fail the required gate.

A separate reviewer scorer reports missed defects and false alarms from actual model output. It withholds rates for incomplete reviews and requires per-case evidence. **Passing sanitizer verification is not an AI-review accuracy result.** No independent detection score is claimed yet; human evidence adjudication and held-out cases are required before making performance claims.

## Documentation

- [Build skills](https://learn.chatgpt.com/docs/build-skills)
- [Package a plugin](https://developers.openai.com/plugins/build/plugins)
- [Submit a plugin](https://developers.openai.com/plugins/deploy/submission)

## License

MIT. See [LICENSE](LICENSE).
