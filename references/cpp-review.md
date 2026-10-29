# C++ memory and resource review

## Trace the lifetime, then test the claim

For each relevant resource, identify acquisition, owner, borrowed aliases, ownership transfers, last valid use, and release. Follow early returns, thrown exceptions, cancellation, failed initialization, and callbacks. A raw pointer alone is not a finding: it may be a valid non-owning borrow.

Check specifically:

- `new`/`delete` and `new[]`/`delete[]` pairing; `malloc`/`free`; ownership transfers to containers or APIs; custom deleters and virtual destruction.
- `string_view`, `span`, iterators, references, and captured `this` outliving their source; invalidation after container reallocation, erase, or move. A reference to a still-live object is not automatically dangling after every move.
- Integer overflow or narrowing before allocation, indexing, copying, and length validation; signedness and length-unit mismatches. Widen or validate before arithmetic, not after overflow.
- Partial construction and error cleanup for descriptors, sockets, locks, transactions, and subprocesses. ASan/LSan do not establish that file descriptors or threads are released.
- Cross-thread ownership, object destruction during callbacks, lock order, atomic ordering, and concurrent container mutation. ThreadSanitizer needs a separate supported build and executed interleavings.

Prefer scoped RAII owners, standard containers, and explicit borrowing contracts. Do not mechanically replace every pointer with shared ownership; that can introduce cycles and obscure lifetimes.

## Reproducible evidence

Capture the repository revision, compiler/platform, exact build/run commands, runtime sanitizer settings, triggering input, exit status, and relevant diagnostics. A crash without the expected diagnostic is a failed reproduction, not proof of the claimed bug. A missing runtime or compiler means incomplete verification.

On a compatible Linux Clang toolchain, a small synthetic reproduction can use:

```sh
clang++ -std=c++17 -O0 -g -fno-omit-frame-pointer \
  -fsanitize=address,undefined -fno-sanitize-recover=all \
  -fsanitize-address-use-after-scope repro.cpp -o repro
ASAN_OPTIONS=detect_leaks=1:halt_on_error=1 \
UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1 ./repro
```

Adapt the real project's build system to instrument the relevant targets. Do not pass off a tiny reproduction as a full application test. Supported platforms and diagnostics vary; consult the [Clang AddressSanitizer](https://clang.llvm.org/docs/AddressSanitizer.html), [LeakSanitizer](https://clang.llvm.org/docs/LeakSanitizer.html), and [UndefinedBehaviorSanitizer](https://clang.llvm.org/docs/UndefinedBehaviorSanitizer.html) documentation.

## Regression tests after a confirmed finding

When fixes/tests are requested, create a focused test using synthetic input that reaches the actual faulty path. It should fail on the old code for the claimed reason and pass after the fix. Exercise at least the triggering boundary or error path and the nearest valid behavior. Use the existing test framework; avoid tests that only inspect source text or assume any nonzero exit means the bug was found.

For ownership bugs, validate repeated operation and cleanup on the failing path. For bounds errors, test the exact boundary and an adjacent valid length. For borrowed lifetimes, preserve the real invalidation/destruction event. Keep inputs and runtime bounded. Report tests that were generated but not run separately.

## Finding format

```text
Severity and title:
Revision / file / line:
Resource owner and borrowed aliases:
Trigger and preconditions:
Lifetime or bounds violation:
Build/run commands and observed diagnostic:
Concrete impact (separate observation from inference):
Minimal fix:
Regression test and result:
Unverified paths / platform limits:
```

For structured export, use the same facts as JSON; include commands as arrays and keep `observed`, `inferred`, and `not_run` evidence distinct. Never invent a sanitizer log to fill the template.
