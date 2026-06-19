# NativeReactDemo Deep Review

status: completed

## Scope

Reviewed pull requests #1 through #6 as one release-validation stack. The review
followed startup from `AppDelegate` bundle resolution through file metadata,
bounded content loading, placeholder and module validation, Xcode resource
wiring, Make aliases, the Python baseline, and the hosted workflow.

## Findings and fixes

- PR #6 matched only the placeholder's first and last lines. A registered bundle
  with arbitrary content between those boundaries was falsely rejected. The
  guard now compares the complete normalized checked-in fixture.
- The Python baseline followed symbolic links and used unbounded whole-file
  reads for required text and vendored hashes. It now opens without following
  links, verifies regular-file metadata on the descriptor, enforces limits, and
  streams SHA-256 input.
- Xcode release-bundle validation accepted case variants, traversal, and
  duplicate `.jsbundle` paths as long as canonical text was also present. It now
  requires exactly one `iOS/main.jsbundle` path.
- Hosted project parsing found `xcodebuild` through `PATH`. It now resolves the
  selected developer tool through absolute `/usr/bin/xcrun`.
- PR #1's repository-wide CODEOWNERS and contributor guidance were retained.

## Provenance

- Broad placeholder boundary matching was introduced by commit `4ca86cf` on
  June 15, 2026. Confidence: clear.
- PATH-based Xcode discovery was introduced by commit `e7970c1` on June 10,
  2026. Confidence: clear.
- Required-file symlink following was carried forward from commit `5071c26` on
  June 8, 2026. Confidence: clear.

## Verification

- Root and external-directory `make check`.
- 13 Python unit and hostile mutation cases covering symlinks, oversized reads,
  streamed hashes, case/traversal/duplicate project paths, absolute tool
  resolution, action pins, permission overrides, secret references, and
  checkout credential persistence.
- `xcodebuild -list` and `-showBuildSettings` parsed the project with Xcode
  26.0.1 after a source-only React Native package extraction. The full local
  build was stopped and its disposable DerivedData removed under disk pressure;
  hosted static validation remains authoritative.
- Lock-only npm resolution audited 183 production packages and found 26 known
  vulnerabilities: 6 critical, 17 high, 2 moderate, and 1 low.
- Redacted current-tree and full-history Gitleaks scans found zero findings.
- GitHub reported zero open code-scanning, secret-scanning, and Dependabot alerts.

## Residual risk

- React Native 0.4.2 and its packager are unsupported and unsafe for production
  or untrusted-network use. Repair requires a dedicated breaking migration.
- The iOS 7/8 deployment targets, Objective-C React sources, and vendored retired
  Fabric/Crashlytics binaries are not compatible evidence for a modern release.
- No signed app launch, simulator test run, device run, Metro execution, or
  vendored binary execution was performed.
