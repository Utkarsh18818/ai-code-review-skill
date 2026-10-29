# Review coverage guide

Use the applicable sections; do not force irrelevant tools or categories onto every repository. Cover meaningful failure paths, not just the happy path. Record unassessed areas explicitly.

| Area | Questions to investigate |
| --- | --- |
| Authentication and sessions | Are credentials/tokens verified correctly? Are expiry, logout/revocation, session rotation, reset links, and replay handled? |
| Authorization | Does every sensitive operation check the requesting identity, object ownership, tenant, and role server-side? Can alternate endpoints or bulk operations bypass the check? |
| Injection and parsing | Does untrusted data reach SQL, shell commands, template interpreters, HTML, headers, or unsafe deserializers? Does validation agree with the eventual parser? |
| Network and files | Are URLs, redirects, DNS resolution, archive entries, symlinks, file names, and destination paths constrained at the operation boundary? Can internal endpoints or sensitive files be reached? |
| Browser boundaries | Are context-appropriate output encoding, CSRF protection, origin checks, cookies, and cross-origin settings correct for the actual authentication model? |
| Secrets and privacy | Are credentials embedded, logged, exposed in errors, or included in client bundles? Are sensitive fields over-fetched or retained unnecessarily? Redact all evidence. |
| Cryptography | Are maintained primitives used correctly, including nonce/key handling, secure randomness, authentication, password hashing, and certificate verification? Avoid custom cryptographic designs. |
| Dependencies | Are packages real and from the expected registry? Check lockfile changes, integrity, install scripts, version drift, known advisories, and native transitive dependencies. Distinguish known vulnerable versions from reachable exposure. |
| Memory safety | Check out-of-bounds access, use-after-free, double-free, uninitialized reads, dangling references/views/iterators, mismatched allocation/deallocation, and overflow/truncation in allocation sizes. |
| Ownership and cleanup | Who owns each allocation, handle, descriptor, stream, socket, transaction, lock, and subprocess? Is ownership transferred once? Is cleanup correct after early returns, exceptions, cancellation, and partial initialization? |
| Resource retention | Are caches/queues bounded? Are subscriptions, callbacks, timers, tasks, and connections released? Distinguish intentional bounded retention from growth under repeated operations. |
| Concurrency | Are shared state, lock order, atomic operations, TOCTOU windows, async cancellation, and object lifetimes correct? Can retries or interleavings duplicate charges or corrupt state? |
| Data integrity | Check transaction boundaries, rollback, idempotency, uniqueness enforcement, numeric precision, migration compatibility, and partial-write recovery. |
| Availability | Can input sizes, regexes, recursion, decompression, pagination, fan-out, retries, or uncontrolled allocations exhaust CPU, memory, disk, or connections? |
| Production behavior | Do APIs exist in the installed version? Are errors swallowed, security checks stubbed, or mocks reachable in production? Are secure defaults preserved? |
| Test quality | Do assertions verify observable behavior? Are negative, permission, boundary, malformed-input, cleanup, and regression cases covered where relevant? Did tests get deleted, skipped, or weakened? |
| Review integrity | Did workflows, scanner settings, exclusions, suppressions, or dependency-audit settings change? Could untrusted PR content change the gate or forge evidence? |

## Evidence guidance for memory and resources

- For a suspected leak, identify the resource creation site, ownership, reachable repetition, and missing cleanup path. Prefer a bounded reproduction showing sustained growth or an instrumented report.
- For a suspected lifetime error, trace the resource lifetime and the invalid access. Consider container invalidation and asynchronous callbacks capturing objects that can be destroyed.
- When tools are unavailable, report a well-supported static finding as such. Do not claim a profiler or sanitizer reproduced it.
- For C/C++, use the project's build system to instrument relevant targets and dependencies where supported. Address/undefined checks and thread checks typically require separate builds; verify compiler compatibility. LeakSanitizer availability differs by platform.
- For managed runtimes, distinguish heap retention from leaking native resources, blocked tasks, and connection exhaustion. Garbage collection does not release every external resource deterministically.

Primary tool references, to consult when selecting platform-specific commands:

- [AddressSanitizer](https://clang.llvm.org/docs/AddressSanitizer.html)
- [LeakSanitizer](https://clang.llvm.org/docs/LeakSanitizer.html)
- [ThreadSanitizer](https://clang.llvm.org/docs/ThreadSanitizer.html)
- [UndefinedBehaviorSanitizer](https://clang.llvm.org/docs/UndefinedBehaviorSanitizer.html)
