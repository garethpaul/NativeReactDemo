# Release Bundle Guard Plan

status: completed

## Context

Release builds load React Native JavaScript from the checked-in
`iOS/main.jsbundle`. If that bundle is missing from the app target, startup
should fail closed instead of passing a nil bundle URL into `RCTRootView`.

## Objectives

- Preserve DEBUG-only localhost packager loading.
- Preserve release `main.jsbundle` loading from the app bundle.
- Return safely from app launch when no JavaScript bundle URL is available.
- Extend `make check` so future bootstrap changes preserve the release bundle
  guard.

## Verification

- `make check`
- `npm run check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
