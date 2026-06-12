# Vendored Framework Integrity

status: completed

## Problem

The repository commits Fabric and Crashlytics framework binaries plus three
executable build tools. The Xcode project can execute this vendored code, but
the static gate has no integrity record to detect accidental or unexplained
binary replacement.

## Scope

- Record SHA-256 hashes for the Fabric and Crashlytics binaries.
- Cover the Fabric `run` tool and Crashlytics `run` and `submit` tools.
- Parse the manifest strictly and reject malformed, duplicate, missing, extra,
  or mismatched entries.
- Keep integrity distinct from provenance, support status, and runtime safety.
- Add mutation verification without executing the vendored binaries.

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- mutate a recorded hash and require the gate to fail
- `git diff --check`

## Work Completed

- Added `VENDORED_FRAMEWORKS.sha256` for the two framework binaries and three
  executable helper tools.
- Added strict format, duplicate, allowlist, completeness, and SHA-256 checks.
- Kept hosted validation read-only and avoided executing vendored artifacts.
- Added project, security, vision, and changelog guidance that distinguishes
  integrity verification from provenance and support.
