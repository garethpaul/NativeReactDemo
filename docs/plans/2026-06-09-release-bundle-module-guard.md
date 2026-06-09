# Release Bundle Module Guard

status: completed

## Context

Release startup already fails closed when `main.jsbundle` is missing, blank, or
the checked-in placeholder. A malformed but non-empty bundle could still reach
`RCTRootView` without registering the `WowNativeReact` module expected by
`AppDelegate`.

## Objectives

- Treat release bundle contents without `AppRegistry.registerComponent` as
  unsafe.
- Require the expected `WowNativeReact` module name before creating
  `RCTRootView`.
- Preserve DEBUG-only localhost packager behavior.
- Extend the static baseline and docs for the bundle module guard.

## Verification

- `python3 scripts/check-baseline.py`
- `make check`
- `git diff --check`
