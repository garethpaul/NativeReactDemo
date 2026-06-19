# Match the Release Placeholder by Shape

status: completed

## Problem

Release validation currently treats any registered JavaScript bundle containing
the phrase `Offline JS file is empty` as the checked-in placeholder. A valid
generated bundle can therefore fail startup because an unrelated string,
comment, fixture, or error message happens to contain that phrase.

## Requirements

- Continue rejecting the exact checked-in placeholder before creating
  `RCTRootView`.
- Recognize the placeholder through its normalized leading comment and terminal
  throw statement rather than an unrestricted marker substring.
- Allow otherwise valid registered bundles that contain the marker phrase in
  unrelated content.
- Preserve nil, file-URL, regular-file, size, UTF-8, blank-content, exact module
  registration, DEBUG packager, and release resource guards.
- Add Objective-C regressions for the checked-in placeholder and a valid bundle
  containing the marker phrase.
- Extend portable checker contracts and maintenance guidance.

## Implementation Units

### U1: Placeholder-shape helper

Files:

- `iOS/AppDelegate.m`

Add named constants for the checked-in placeholder header and terminal throw.
Use a small content helper after trimming so both boundaries must match before
the bundle is classified as the placeholder.

### U2: Regression coverage

Files:

- `WowNativeReactTests/WowNativeReactTests.m`

Expose the existing private validation method through a test-only category.
Write temporary regular bundle files and assert that the checked-in placeholder
is rejected while a registered bundle containing the marker phrase elsewhere
is accepted.

### U3: Contracts and evidence

Files:

- `scripts/check-baseline.py`
- `README.md`
- `SECURITY.md`
- `VISION.md`
- `CHANGES.md`
- `docs/plans/2026-06-15-release-placeholder-shape-guard.md`

Require boundary-based placeholder recognition, both regression methods,
completed evidence, and project guidance.

## Verification

- Run focused source/test contracts and every Make gate from the checkout and
  an external directory with explicit timeouts.
- Run hosted XCTest through the existing canonical workflow after push.
- Reject mutations that restore substring matching, remove either boundary,
  weaken either regression, remove guidance, or reopen the plan.
- Audit the exact diff, Objective-C/checker syntax, Xcode project integrity,
  generated artifacts, credential patterns, conflict markers, binaries, large
  files, and intended paths before commit.

## Risks

- The shape deliberately follows the checked-in placeholder file; future
  placeholder text changes must update the constants and regression together.
- The helper remains a startup preflight, not a general JavaScript parser.
- The stacked base pull request must remain available and merge first.

## Verification Results

- Focused source and test contracts, Python checker compilation with external
  bytecode output, and `git diff --check` passed.
- Root and external-directory Make gates passed on Linux; `xcodebuild` was
  unavailable locally, so the existing hosted macOS workflow remains the
  authoritative Objective-C/Xcode validation.
- Seven isolated hostile mutations were rejected: unrestricted substring
  matching, removal of either content boundary, weakening either regression,
  missing maintenance guidance, and a reopened plan.
