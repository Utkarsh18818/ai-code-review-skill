# Enforcing review outside the skill

A skill guides an agent; it cannot force every contributor to invoke it, prove the reviewer is correct, or stop an administrator who controls repository policy. Use repository controls and independent checks for enforcement. This package does not install or configure a CI gate.

## Repository controls

1. Require pull requests and independent approval for protected branches. Dismiss stale approvals or require approval of the latest reviewable push. Restrict direct pushes and force pushes.
2. Require relevant build/tests, security scanning, dependency auditing, and memory/resource checks for the supported stack. Configure checks for the current revision or merge candidate; previous revisions are not evidence for newly changed code.
3. Use an always-running aggregation job as the required gate when child jobs are conditional. Make it explicitly fail for required checks that fail, time out, are cancelled, are missing, or are unexpectedly skipped. An unassessed category needs an explicit policy decision; never silently convert it into success.
4. Bind required status checks to the expected trusted GitHub App where supported. Use unique check names. Do not trust a committed JSON report or an agent's self-declared disposition as proof that tests ran.
5. Protect workflow files, review policy, CODEOWNERS, scanner configuration, and suppressions with independent ownership/review. Where available, enforce workflows from organization-controlled policy that a PR author cannot replace.
6. Apply protections to administrators and remove bypass allowances where supported. Limit who can change repository rules. Owners with authority to change those settings remain a trust boundary; monitor rule changes.
7. Keep credentials away from untrusted pull-request execution. Use least-privilege permissions and isolated runners. Do not run untrusted PR code in a privileged workflow just to obtain a review result.
8. Define exception authority, scope, justification, expiry, and audit evidence outside the skill. An exception must not erase the original finding or masquerade as a clean scan.

Build a stack-specific CI configuration after identifying the repository's languages, build system, existing checks, hosting plan, and permissions. No generic workflow can honestly establish all of these properties for every project.

## Verify the enforcement

In a disposable branch/repository, verify that a failing required check blocks merging; missing/skipped/cancelled child checks fail the aggregate; a new commit invalidates old evidence; a PR cannot weaken its own trusted gate; and untrusted runs cannot access secrets. Inspect actual repository settings, not just committed workflow files.

## Primary documentation

- [Protected branches and bypass settings](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [Status checks, including skipped jobs](https://docs.github.com/en/pull-requests/reference/status-checks)
- [Required checks and the latest commit](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks)
