# Exact Module Token Boundary

status: completed

## Problem

The release bundle guard searched for `AppRegistry.registerComponent` followed
by the expected quoted module-name prefix, but the search string stopped before
the closing quote and argument delimiter. A bundle registering
`WowNativeReactPreview` could therefore satisfy the `WowNativeReact` check.

## Design

- Match the expected module name through its closing quote and following comma.
- Preserve both single-quoted and double-quoted React Native registrations.
- Add native coverage for a longer prefix name.
- Keep portable source validation aligned with the native implementation.

## Test-First Evidence

The portable contract and native regression were added before the production
change. The contract failed against the original prefix match and passed after
both registration patterns required the complete first argument.

## Verification

- `python3 scripts/check-baseline.py`
- `python3 -m unittest discover -s tests -p 'test_*.py'`
- `make check`
- external-directory `make check`
- hostile prefix-pattern mutation
- `git diff --check`

Native XCTest and app launch remain a separate macOS/Xcode validation boundary.
