# Native React Demo Baseline Plan

status: completed

## Context

`NativeReactDemo` is an early React Native iOS sample with React Native 0.4,
Objective-C app bootstrap code, a checked-in `main.jsbundle`, and vendored
Fabric/Crashlytics frameworks.

## Risks

- `package.json` allowed React Native drift through a caret range.
- App startup always loaded JavaScript from the localhost packager, which is
  only appropriate for debug builds.
- The JavaScript sample included an unused insecure HTTP asset URL.
- The app plist had an empty location permission string even though the sample
  does not use location.
- There was no host-portable verification path for Linux or non-Xcode review.

## Work Completed

- Pinned React Native to `0.4.2`.
- Gated localhost bundle loading to `DEBUG` and used `main.jsbundle` otherwise.
- Removed the unused HTTP mocked image data and the empty location usage string.
- Added local xcconfig/env ignore rules for credential hygiene.
- Added `Makefile`, `npm run check`, and `scripts/check-baseline.py`.

## Verification

- `make check`
- `npm run check`
- `git diff --check`
