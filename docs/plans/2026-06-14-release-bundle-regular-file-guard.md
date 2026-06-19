# Release Bundle Regular-File Guard

status: completed

## Summary

Require the release JavaScript bundle to be a regular file before trusting its
metadata, applying the 10 MiB bound, or reading its contents.

## Problem Frame

The release guard reads `NSFileSize` from `attributesOfItemAtPath:` but does not
inspect `NSFileType`. Foundation reports symbolic links as
`NSFileTypeSymbolicLink`; accepting that entry permits the small link metadata
to pass before `stringWithContentsOfURL:` follows the target and reads it.

## Requirements

- Reject missing, symbolic-link, directory, and other non-regular bundle items.
- Perform the file-type check before size comparison and content loading.
- Preserve the 10 MiB limit, UTF-8 parsing, placeholder, blank, module
  registration, release-only, and debug packager behavior.
- Extend SDK-free static contracts and maintained documentation.

## Key Technical Decisions

- Use the existing `attributesOfItemAtPath:` result and require `NSFileType` to
  equal `NSFileTypeRegular`; do not resolve links before validation.
- Keep the failure closed and silent by returning the existing unsafe-bundle
  result.

## Implementation Units

### U1: Require a regular release bundle

**Files:** `iOS/AppDelegate.m`, `scripts/check-baseline.py`

**Approach:** Add a static contract for type extraction, regular-file equality,
and ordering before the size and content reads, then implement that guard.

**Execution note:** Add the failing static contract before Objective-C changes.

**Test scenarios:**

- Missing `NSFileType` fails closed.
- Symbolic links and other non-regular items are rejected before size or content
  access.
- Removing the type check or moving it after the content read fails validation.

**Verification:** The baseline fails against the current source, then all Make
aliases pass after implementation.

### U2: Record evidence and operator guidance

**Files:** `README.md`, `SECURITY.md`, `VISION.md`, `CHANGES.md`,
`docs/plans/2026-06-14-release-bundle-regular-file-guard.md`

**Approach:** Document the regular-file boundary and completed SDK-free
verification without claiming an unavailable build or simulator run.

**Test scenarios:**

- Targeted hostile mutations reject type-check, ordering, documentation, and
  plan drift.

**Verification:** All gates, mutations, diff, artifact, and credential audits
pass.

## Scope Boundaries

- Do not execute vendored framework scripts or npm install.
- Do not change debug packager loading or JavaScript bundle contents.
- Do not upgrade React Native, Xcode project formats, or retired frameworks.

## Sources

- Apple Foundation `attributesOfItemAtPath:` documentation: symbolic links are
  reported through the `NSFileType` attribute as `NSFileTypeSymbolicLink`.

## Work Completed

- Read `NSFileType` from the existing release bundle attribute dictionary and
  rejected missing or non-regular values before the size comparison.
- Preserved the existing 10 MiB, UTF-8, placeholder, blank, module, release,
  and debug-packager behavior.
- Extended the SDK-free checker and maintained documentation with a per-file
  regular-bundle contract.

## Verification Completed

- `make lint`, `make test`, `make build`, and `make check` passed from the
  checkout, and the absolute Makefile check passed from an external directory.
- The static contract failed against the original source before the Objective-C
  guard was added.
- Five hostile mutations covering type extraction/order, regular-file equality,
  missing-type handling, documentation, and completed plan evidence were
  rejected.
- `xcodebuild` was unavailable; no app build, signing, simulator, npm install,
  vendored script execution, or React Native runtime flow was performed.
