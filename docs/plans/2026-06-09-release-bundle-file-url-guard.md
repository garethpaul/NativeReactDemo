# Release Bundle File URL Guard

status: completed

## Context

Release startup loads the checked-in `main.jsbundle` before creating the React
Native root view. Existing guards fail closed on nil, placeholder, blank, or
malformed bundle contents, but the helper did not explicitly require a local
file URL.

## Objectives

- Fail closed when release bundle validation receives a non-file URL.
- Preserve DEBUG-only localhost packager loading.
- Preserve existing placeholder, blank, and module registration guards.
- Extend the SDK-free static baseline and docs for the release bundle file URL
  guard.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
