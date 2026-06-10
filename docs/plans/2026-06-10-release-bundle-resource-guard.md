# Release Bundle Resource Guard

status: completed

## Context

Release startup loads `main.jsbundle` from the app bundle before creating the
React Native root view. Existing guards fail closed when the URL, contents, or
module registration are unsafe, but the static baseline should also catch Xcode
project drift that stops packaging `iOS/main.jsbundle` into app resources.

## Objectives

- Verify the Xcode project still references `iOS/main.jsbundle`.
- Verify `main.jsbundle` remains in the app target Resources phase.
- Preserve existing release bundle URL, placeholder, blank, and module guards.
- Extend SDK-free docs and baseline checks for the resource wiring guard.

## Verification

- `scripts/check-baseline.py`
- `make check`
- `git diff --check`
