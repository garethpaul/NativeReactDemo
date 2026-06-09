# Exact Bundle Registration Guard

status: completed

## Context

Release startup validates `main.jsbundle` before creating the React Native root
view. The existing module guard checked for the registration call and module
name as independent strings, which could accept malformed bundle contents that
mention both without registering the launched module.

## Objectives

- Require `AppRegistry.registerComponent` to register the launched
  `WowNativeReact` module.
- Use one module-name constant for bundle validation and `RCTRootView` startup.
- Preserve DEBUG-only localhost packager loading and local release bundle
  checks.
- Extend the SDK-free static baseline and docs for exact registration
  guardrails.

## Verification

- `python3 scripts/check-baseline.py`
- `make check`
- `git diff --check`
