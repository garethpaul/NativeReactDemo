# Changes

## 2026-06-26 03:58 PDT

- **Priority:** P2 developer workflow clarity.
- **Summary:** Completed the NativeReactDemo setup and manual-launch priorities
  with source-backed legacy compatibility, debug packager, release placeholder,
  simulator checklist, and hosted-verification guidance.
- **Work:** Added fail-closed README, roadmap, history, and completed-plan
  contracts without changing runtime, dependencies, project settings, or CI.
- **Threads:** None; active work in other repositories was excluded.
- **Files:** Updated `README.md`, `VISION.md`, `CHANGES.md`, the static checker,
  and `docs/plans/2026-06-26-native-react-setup-guide.md`.
- **Validation:** The initial checker failed on the absent guide. All 15 final
  hostile mutations failed closed; two preliminary runs exposed duplicate
  version/command mentions and one wrapped fixture, which strengthened the
  unique contracts without changing runtime behavior. Root and external
  `/usr/bin/make check` each passed 42 Make authority cases and 14 Python tests;
  Xcode remained unavailable and the static baseline reported that honestly.
- **Findings:** No current Node/Xcode combination is promised; the checked-in
  iOS 7/8.2 and React Native 0.4.2 metadata is historical, and Release remains
  intentionally non-runnable with the placeholder.
- **Blockers:** A real launch requires an isolated compatible legacy runtime.
- **Next action:** Prove all guide drift fails closed and require exact-head CI.

## 2026-06-25 08:59 PDT

- **Priority:** P1 release startup correctness.
- **Summary:** Tightened React Native module validation so a bundle registering
  a longer prefix name cannot pass as `WowNativeReact`.
- **Work:** Required the closing quote and first-argument comma for single- and
  double-quoted registrations, added native prefix-regression coverage, and
  strengthened the portable source contract.
- **Threads:** No open issue or pull request covered this release guard gap.
- **Files:** Updated `iOS/AppDelegate.m`, native tests, portable validation,
  contributor/security guidance, and a completed maintenance plan.
- **Validation:** The test-first portable contract failed against the prefix
  match; a hostile source mutation, root and external-directory `make check`,
  14 Python tests, and `git diff --check` then passed. Native XCTest and project
  parsing were skipped because `xcodebuild` is unavailable.
- **Findings:** The prior substring ended at the expected module name and could
  accept `WowNativeReactPreview` or any other longer prefix name.
- **Blockers:** Native XCTest requires compatible macOS/Xcode and the legacy
  React Native source environment.
- **Next action:** Review the exact PR head and merge only after hosted checks
  pass.

## 2026-06-21

- Bound Make verification authority, rejected non-executing modes and
  additional Make programs, and isolated Python verification startup.
- Preserved the complete checkout root for absolute Makefile paths containing
  spaces, brackets, or apostrophes, and rejected `MAKEFILE_LIST` overrides.
- Expanded the SDK-free suite from 13 to 16 tests with hostile-path and root
  override regression coverage.

## 2026-06-19

- Replaced broad release placeholder boundary matching with exact normalized
  fixture matching and added a boundary-collision regression test.
- Added no-follow bounded reads and streamed hashes for required repository
  files and vendored artifacts.
- Rejected case variants, traversal, and duplicate Xcode release bundle paths.
- Resolved Xcode through absolute `/usr/bin/xcrun` and added 13 unit/hostile
  tests for file, project, tool, workflow permission, action pin, secret, and
  checkout credential invariants.
- Added repository-wide ownership guidance and recorded the unsupported React
  Native 0.4.2 audit result: 26 production vulnerabilities, including 6 critical.

## 2026-06-14

- Added a release placeholder shape guard so valid registered bundles may
  mention the placeholder error text without being rejected.
- Added a release bundle regular-file guard so symbolic links and other
  non-regular resources fail before size or content access.

## 2026-06-13

- Made every SDK-free Make alias resolve the static checker from the checkout
  when the Makefile is invoked by absolute path.

## 2026-06-12

- Disabled persisted checkout credentials and enforced the sole pinned
  credential-free workflow boundary.

## 2026-06-10

- Added a release bundle size guard that rejects missing file metadata or more
  than 10 MiB before reading local JavaScript contents.
- Added vendored framework integrity verification for Fabric, Crashlytics, and
  their executable build tools using a strict SHA-256 manifest.
- Added pinned, read-only macOS hosted validation for the static release-bundle
  baseline and `WowNativeReact.xcodeproj` parsing.
- Added a release bundle resource guard so the static baseline catches Xcode
  project changes that stop packaging `iOS/main.jsbundle`.

## 2026-06-08

- Added `make lint`, `make test`, and `make build` aliases so the standard
  gate commands run the same SDK-free static baseline as `make check`.
- Added a bundle module guard so release startup fails closed when a bundle does
  not register `WowNativeReact`.
- Added a release bundle file URL guard so release startup fails closed on
  non-local JavaScript bundle URLs.
- Added an exact bundle registration guard so release startup requires
  `AppRegistry.registerComponent` to register the launched module name.
- Added a bundle module name guard so registration checks fail closed when the
  expected module name is blank.
- Added `make check` and `npm run check` static verification for the legacy React Native iOS sample.
- Pinned the React Native dependency to `0.4.2` for reproducible legacy installs.
- Gated localhost packager bundle loading to debug builds and kept release builds pointed at `main.jsbundle`.
- Added a release bundle guard before creating the React Native root view.
- Added a placeholder bundle guard so release startup fails closed when `main.jsbundle` is still the checked-in placeholder.
- Added a blank bundle guard so release startup fails closed on missing, empty, or whitespace-only bundle contents.
- Removed an unused insecure HTTP image URL from the JavaScript sample.
- Removed the empty location usage string and added local secret/config ignore rules.
- Aligned the Xcode UI test with the rendered `Hi` text.
- Broadened the Xcode UI test to recognize both attributed and plain text views.
- Documented Fabric/Crashlytics credential handling and release bundle ownership.
