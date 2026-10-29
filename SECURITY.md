# Security policy

Do not put credentials, private source, or working attacks against live services in public issues. Use GitHub private vulnerability reporting when enabled; otherwise contact the repository owner privately before disclosing sensitive details.

The skill and CI do not guarantee vulnerability-free code. CI checks this repository's Python utilities and Actions workflows, plus package structure and tests. It does not automatically review other repositories or perform dynamic memory analysis on them.

The required gate blocks every reported CodeQL result, malformed/missing analysis, and unsuccessful prerequisite job. Changes to workflow, checker, ownership, and policy require independent review under branch protection. Repository owners who can edit protection rules remain trusted administrators.

No third-party Python dependencies are used by the utilities. GitHub Actions are pinned to upstream commit SHAs; review action updates before merging. Adding dependencies or a new implementation language requires an accompanying audit/scanning strategy. Adding native code requires appropriate memory/resource tests; a green Python scan is not native-code coverage.
