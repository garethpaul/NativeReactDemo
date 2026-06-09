# Bundle Module Name Guard

status: completed

## Context

Release startup now checks that `main.jsbundle` registers the same React Native
module that `RCTRootView` launches. The helper rejected nil module names, but a
blank or whitespace-only expected module name should also fail closed before
building registration signatures.

## Objectives

- Trim the expected module name before release bundle registration checks.
- Reject blank or whitespace-only module names.
- Preserve exact single-quoted and double-quoted `AppRegistry.registerComponent`
  checks for `WowNativeReact`.
- Extend the SDK-free baseline and docs so the helper remains fail-closed.

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- `git diff --check`
