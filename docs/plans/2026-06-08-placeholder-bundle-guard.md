# Placeholder Bundle Guard Plan

status: completed

## Context

Release builds already resolve `iOS/main.jsbundle` instead of the localhost packager and fail closed when the bundle URL is unavailable. The checked-in bundle is an intentional placeholder that throws at runtime if it reaches React Native startup.

## Objectives

- Detect the checked-in empty `main.jsbundle` placeholder before creating `RCTRootView`.
- Keep the placeholder bundle guard out of debug builds so the localhost packager flow is unchanged.
- Preserve the existing nil bundle URL guard.
- Extend the static baseline and docs to keep placeholder bundle guard behavior visible.

## Verification

- `make check`
- `git diff --check`
