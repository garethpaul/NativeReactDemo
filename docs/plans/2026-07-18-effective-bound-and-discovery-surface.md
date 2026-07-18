# Effective Release Bound and Closed Discovery Surface

status: completed

## Problem

Two verification gaps let a real defect ship at exit 0.

First, the release bundle size bound was pinned by spelling rather than by
value. `main` located the limit with
`app_delegate.find("MaximumReleaseBundleBytes = 10ULL * 1024ULL * 1024ULL")`
and the comparison with
`app_delegate.find("[bundleSize unsignedLongLongValue] > MaximumReleaseBundleBytes")`.
Both are substring probes, so appending a factor at either site preserved the
pinned text while widening the effective bound 1024x to 10 GiB, and `make check`
exited 0. The same pin rejected `MaximumReleaseBundleBytes = 10485760ULL`, which
is byte-for-byte the same limit. The verdicts inverted: the checker read text,
not meaning.

Second, the unittest discovery surface was open. `REQUIRED` pins the contents of
`tests/__init__.py` and `tests/test_check_baseline.py`, but nothing constrained
the absence of other files, and contents cannot be pinned for a file that does
not exist. `python3 -I -B -m unittest discover -s tests` imports every
`test_*.py` under `tests/`, including nested packages. A new
`tests/test_aaa_shadow.py` that rebinds `unittest.TestCase.assertEqual` to a
no-op edited no pinned file, left the `EXPECTED_MAKEFILE_SHA256` intact, and
turned a genuinely caught defect green:

```
defect planted, no added file            FAILED (failures=1)  exit 2
same defect + tests/test_aaa_shadow.py   OK                   exit 0
```

This matters because the repository's documented posture, recorded in
`docs/plans/2026-06-27-lexical-module-registration.md`, deliberately relies on
the portable Python tests as the substitute for native XCTest that the
maintained baseline does not execute. An unpinned assertion mechanism in the
substitute control removes the compensating check the posture depends on.

## Options

1. Keep substring pins and add more literals. Rejected: an append defeats any
   prefix pin, and a second definition defeats a whole-line pin.
2. Compare the effective bound and close the discovery surface. Chosen: it
   accepts equivalent spellings, rejects widening at either site, and cannot be
   bypassed by adding a file.
3. Compile and run the Objective-C target to observe the bound at runtime.
   Rejected for the reason already recorded in the lexical registration plan: a
   full React Native 0.4.2 build is not reproducible in this scope, and a
   synthetic-header compile would not represent the real dependency graph.

## Decision

Parse the bound's definition with an anchored whole-line pattern, require
exactly one definition, and evaluate the constant expression with a bounded
evaluator that accepts only decimal literals joined by addition and
multiplication. Compare the result against the checker's existing
`MAXIMUM_RELEASE_BUNDLE_BYTES`, which already held the correct value. Require
exactly one anchored whole-line use-site comparison so the bound cannot be
widened where it is read. Preserve the existing fail-closed ordering chain by
deriving its indices from the anchored matches.

Close the world on `tests/` with a recursive inventory against
`EXPECTED_TEST_ENTRIES`, mirroring the existing
`.github/workflows` inventory idiom. The inventory is recursive and excludes
nothing: `unittest` discovery recurses into nested packages, and a test placed
in `tests/sub/` or even `tests/__pycache__/` is discovered and executed, so a
non-recursive or `__pycache__`-exempt inventory would leave the bypass open.

## Verification

Measured with the canonical gate, both directions, against the base branch and
then the fix.

| Mutation | Effective bound | Base | Fixed |
| --- | --- | --- | --- |
| clean tree | 10 MiB | exit 0 | exit 0 |
| `10485760ULL` (same value, different spelling) | 10 MiB | exit 2 rejected | exit 0 accepted |
| `* 1024ULL` appended at definition | 10 GiB | exit 0 shipped | exit 1 rejected |
| `* 1024ULL` appended at use site | 10 GiB | exit 0 shipped | exit 1 rejected |
| second definition at 10 GiB | 10 GiB | exit 0 shipped | exit 1 rejected |
| comparison removed (`NO`) | unbounded | exit 1 | exit 1 |
| `tests/test_aaa_shadow.py` no-op assertions | n/a | exit 0 shipped | exit 1 rejected |
| `tests/sub/` nested shadow package | n/a | exit 0 shipped | exit 1 rejected |

The widened bounds were confirmed by compiling the arithmetic:
`10ULL * 1024ULL * 1024ULL * 1024ULL` is 10737418240 bytes (10240 MiB).

The new checks are covered by live tests rather than by their own presence.
Gutting `release_bundle_bound_errors` to `return []` fails 4 of the new tests;
gutting `discovery_inventory_errors` to `return []` fails 3. Canonical
`make check` passes 42 Make authority cases and 39 Python tests, up from 26.

Skipped platform validation, unchanged from the existing baseline: `xcodebuild`
is unavailable in this environment, so the static iOS baseline ran alone. The
maintained gate still does not compile the Objective-C target or execute native
XCTest, so the runtime behavior of `MaximumReleaseBundleBytes` is verified by
source analysis only, and defects reachable only at Objective-C runtime remain
outside the gate's observation. That limitation is unchanged by this plan and
remains as recorded in the lexical module registration plan.
