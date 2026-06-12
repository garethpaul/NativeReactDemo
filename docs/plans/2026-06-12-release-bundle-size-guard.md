# Release Bundle Size Guard

status: planned

## Context

Release startup validates `main.jsbundle` by reading the complete local file
into an `NSString`. Existing guards cover nil, non-file, unreadable, blank,
placeholder, and wrong-module bundles, but a corrupted or accidentally huge
resource can still amplify startup memory before validation.

## Priorities

1. Reject release bundles larger than 10 MiB before reading contents.
2. Fail closed when file attributes or a numeric file size are unavailable.
3. Preserve DEBUG localhost loading and all existing release validation.
4. Protect the ordering with the SDK-independent baseline checker.

## Implementation Units

### Release Bundle Validation

File: `iOS/AppDelegate.m`

Read local file attributes after the file-URL guard and before reading bundle
contents. Treat missing metadata or sizes above 10 MiB as placeholders so
release launch returns `NO` through the existing fail-closed path.

### Static Contract And Documentation

Files:

- `scripts/check-baseline.py`
- `README.md`
- `SECURITY.md`
- `VISION.md`
- `CHANGES.md`
- `docs/plans/2026-06-12-release-bundle-size-guard.md`

Require the limit, fail-closed metadata handling, and pre-read ordering while
documenting that hosted validation parses the Xcode project but does not launch
the legacy app.

## Verification

- `python3 -m py_compile scripts/check-baseline.py`
- `make lint`
- `make test`
- `make build`
- `make check`
- hostile mutations removing the size limit, metadata guard, or pre-read ordering
- `git diff --check`
- hosted push and pull-request checks

## Boundaries

- Do not regenerate or replace `iOS/main.jsbundle` in this change.
- Do not change DEBUG packager loading or the expected module name.
- Do not claim simulator/runtime coverage without Xcode execution.
