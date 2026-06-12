# NativeReactDemo

<!-- README-OVERVIEW-IMAGE -->
![Project overview](docs/readme-overview.svg)

## Overview

`garethpaul/NativeReactDemo` is an Apple platform application or Objective-C/Swift sample. NativeReactDemo

This README is based on the checked-in source, manifests, scripts, and repository metadata on the `master` branch. The project language mix found during review was: C/C++ headers (7), Objective-C (3), JavaScript (1).

## Repository Contents

- `README.md` - project overview and local usage notes
- `package.json` - JavaScript dependency and script metadata
- `Crashlytics.framework` - source or example code
- `Fabric.framework` - source or example code
- `iOS` - source or example code
- `SECURITY.md` - security reporting and disclosure guidance
- `VISION.md` - project direction and maintenance guardrails
- `WowNativeReact.xcodeproj` - Xcode project file
- `WowNativeReactTests` - source or example code

Additional scan context:

- Source directories: Crashlytics.framework, Fabric.framework, WowNativeReactTests, iOS
- Dependency and build manifests: package.json
- Entry points or build surfaces: WowNativeReact.xcodeproj, package.json
- Test-looking files: WowNativeReactTests/Info.plist, WowNativeReactTests/WowNativeReactTests.m

## Getting Started

### Prerequisites

- Git
- macOS with Xcode for building Apple platform projects
- Node.js and npm

### Setup

```bash
git clone https://github.com/garethpaul/NativeReactDemo.git
cd NativeReactDemo
npm install
make lint
make test
make build
make check
```

The setup commands above are derived from repository files. Legacy mobile, Python, or JavaScript samples may require older SDKs or package versions than a modern workstation uses by default.

## Running or Using the Project

- Open `WowNativeReact.xcodeproj` in Xcode, choose the app or sample scheme, and run it on the matching simulator/device.
- Run `npm start` for the default development command.

Detected npm scripts:

- `npm run start` - `node_modules/react-native/packager/packager.sh`

## Testing and Verification

- `make lint`, `make test`, `make build`, and `make check` run the SDK-free
  static baseline.
- Pinned `macos-15` GitHub Actions runs that baseline and parses
  `WowNativeReact.xcodeproj` without npm install, credentials, vendored script
  execution, build, signing, simulator launch, or application execution.
- `npm run check`
- Xcode's test action or `xcodebuild test` with the appropriate scheme and destination

When the required SDK or runtime is unavailable, use static checks and source review first, then verify on a machine that has the matching platform toolchain.
The static check verifies React Native pinning, DEBUG-only localhost bundle loading,
release `main.jsbundle` wiring, the release bundle guard, the blank bundle guard, plist/XML validity, and local secret ignore rules.

## Configuration and Secrets

- Fabric/Crashlytics credentials, signing material, local xcconfig files, `.env` files, and private endpoints should stay out of git.
- Release builds load `iOS/main.jsbundle`; the checked-in bundle is a
  placeholder, so regenerate it intentionally when JavaScript changes need to
  ship without the packager.
- The release bundle guard returns safely during launch if no JavaScript bundle URL is available.
- The placeholder bundle guard also fails closed if release startup resolves the checked-in empty bundle.
- The blank bundle guard treats missing, empty, or whitespace-only release bundle content as an unsafe placeholder.
- The bundle module guard treats release bundles without the expected `WowNativeReact` registration as unsafe.
- The release bundle file URL guard rejects non-local release bundle URLs before
  React Native startup.
- The exact bundle registration guard requires the release bundle to register
  the same `WowNativeReact` module used to create `RCTRootView`.
- The bundle module name guard fails registration checks closed if the expected
  React Native module name is blank or whitespace-only.
- The release bundle resource guard keeps `iOS/main.jsbundle` wired into the
  app target resources that release startup loads.
- The release bundle size guard rejects local bundles larger than 10 MiB or
  missing file-size metadata before reading JavaScript contents.

## Security and Privacy Notes

- Review changes touching authentication or token handling; examples from the scan include Crashlytics.framework/Headers/CLSLogging.h, Crashlytics.framework/Headers/CLSReport.h.
- Review changes touching external API calls or credential-adjacent configuration; examples from the scan include Crashlytics.framework/Headers/Crashlytics.h, Fabric.framework/Headers/FABAttributes.h, Fabric.framework/Headers/Fabric.h, Fabric.framework/Info.plist.
- Review changes touching network requests, sockets, or service endpoints; examples from the scan include Crashlytics.framework/Headers/Crashlytics.h, Fabric.framework/Info.plist, WowNativeReactTests/Info.plist, iOS/AppDelegate.m, and 2 more.
- Keep the release bundle guard in place when changing `iOS/AppDelegate.m` bundle loading.
- Keep the release bundle file URL guard in place so release startup only uses
  a local `main.jsbundle`.
- Keep the exact bundle registration guard in place so malformed release
  bundles cannot satisfy module checks with unrelated strings.
- Keep the bundle module name guard in place so blank expected module names do
  not satisfy release bundle checks.
- Keep the release bundle resource guard in place so release builds still ship
  the local `main.jsbundle` file.
- Keep the release bundle size guard in place so corrupted or accidentally huge
  resources cannot be read into memory before validation.
- Vendored framework integrity checks verify the recorded SHA-256 hashes for
  Fabric, Crashlytics, and their executable build tools before project parsing.
- Review changes touching mobile permissions or privacy-sensitive device data; examples from the scan include Crashlytics.framework/Headers/Crashlytics.h.
- Review changes touching file, media, JSON, XML, CSV, OCR, or data parsing; examples from the scan include Crashlytics.framework/Headers/Crashlytics.h, Fabric.framework/Info.plist, WowNativeReactTests/Info.plist, iOS/Info.plist, and 1 more.

## Maintenance Notes

- This looks like an Apple platform project or sample. Xcode, Swift, CocoaPods, and deployment target versions may need to match the original project era.
- Run `make lint`, `make test`, `make build`, and `make check` before pushing
  JavaScript, plist, Xcode project, dependency, or security documentation
  changes.
- See `docs/plans/2026-06-09-make-gate-aliases.md` for the local gate alias
  baseline.
- See `docs/plans/2026-06-09-bundle-module-name-guard.md` for the bundle module
  name guardrail.
- See `SECURITY.md` for vulnerability reporting and safe research guidance.
- See `VISION.md` for project direction and contribution guardrails.

## Contributing

Keep changes small and tied to the project that is already present in this repository. For code changes, document the toolchain used, avoid committing generated dependency directories or local configuration, and update this README when setup or verification steps change.
