# Hosted Project Validation

status: completed

## Context

The repository has an SDK-free baseline for release bundle loading, module
registration, placeholder rejection, Xcode resources, credentials, and project
wiring, but no hosted validation. React Native 0.4.2 has no committed lockfile,
so a modern npm install would not be reproducible.

## Priorities

1. Run the canonical static gate on pinned macOS CI.
2. Parse `WowNativeReact.xcodeproj` whenever Xcode is available.
3. Enforce a read-only, bounded workflow from the baseline checker.
4. Keep npm install, credentials, vendored scripts, build, signing, simulator,
   and application execution outside hosted validation.

## Implementation Units

Files:

- `.github/workflows/check.yml`
- `scripts/check-baseline.py`
- `README.md`
- `VISION.md`
- `SECURITY.md`
- `CHANGES.md`

Add push, pull-request, and manual triggers; read-only permissions; concurrency
cancellation; a bounded `macos-15` job; commit-pinned checkout; and `make check`.
Require that contract and run `xcodebuild -list -project
WowNativeReact.xcodeproj` when Xcode exists.

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- workflow YAML parse
- `git diff --check`
- successful hosted macOS `Check` workflow for the pushed commit

## Boundaries

- Do not install React Native 0.4.2 or execute the packager in CI.
- Do not provide credentials, run vendored scripts, build, sign, or simulate.
