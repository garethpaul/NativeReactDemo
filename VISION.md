## Native React Demo Vision

This document explains the current state and direction of the project.
Project overview and developer docs: [`README.md`](README.md)

Native React Demo is an early React Native iOS sample with a bundled iOS app,
React Native 0.4-era JavaScript, and Fabric/Crashlytics frameworks.

The repository is useful as a preserved example of early React Native project
layout and iOS integration. Project context lives in [`README.md`](README.md).

The goal is to keep the demo understandable while making legacy dependency and
credential assumptions clear.

Current baseline: `make lint`, `make build`, and `make verify` run
`scripts/check-baseline.py`; `make test` and `make check` add focused hostile
unit tests. The gates verify React Native dependency pinning,
DEBUG-only localhost bundle loading, release `main.jsbundle` wiring, the
release bundle guard, the blank bundle guard, plist/XML validity, local secret
ignores, and Fabric/Crashlytics documentation.

The current focus is:

Priority:

- Preserve the React Native iOS bridge and app structure
- Keep `npm start` and package metadata visible for the old toolchain
- Avoid committing Fabric/Crashlytics credentials or signing material
- Keep localhost packager loading DEBUG-only and release bundle ownership explicit
- Keep the release bundle guard in app startup
- Keep the placeholder bundle guard around checked-in empty release bundles
- Keep the blank bundle guard around missing or whitespace-only release bundles
- Keep the bundle module guard around malformed release bundles
- Keep the release bundle file URL guard around release bundle loading
- Keep the exact bundle registration guard tied to the launched module name
- Require the complete quoted module argument so prefix names cannot pass
- Keep the bundle module name guard before release bundle registration checks
- Keep the release bundle resource guard around Xcode resource wiring
- Keep the release bundle size guard before reading release JavaScript
- Keep the release bundle regular-file guard before size and content access
- Keep the release placeholder shape guard tied to the complete normalized fixture
- Keep vendored framework integrity hashes for Fabric/Crashlytics executables
- Keep no-follow bounded file reads and canonical Xcode bundle paths
- Keep deterministic Xcode resolution through absolute `/usr/bin/xcrun`
- Keep lint, build, and verify on the static baseline and test/check on the hostile suite
- Keep hosted macOS project parsing pinned, read-only, and free of npm install
- Keep hosted source retrieval credential-free after checkout
- Maintain security policy for the sample

Next priorities:

- Add README setup and supported Node/Xcode notes
- Modernize React Native only in a dedicated migration
- Treat the 26 known production dependency vulnerabilities as a release blocker
- Add a manual launch checklist for the iOS app on a matching Xcode simulator
- Regenerate `main.jsbundle` in a dedicated change when JavaScript behavior changes

Contribution rules:

- One PR = one focused React Native, iOS, dependency, or documentation change.
- Keep credentials and generated signing files out of git.
- Verify the app after bridge or bundle changes.
- Do not mix React Native major migrations with app behavior changes.
- Preserve the release bundle guard when changing `AppDelegate` startup.

## Security

Canonical security policy and reporting:

- [`SECURITY.md`](SECURITY.md)

Crash-reporting credentials and signing material must remain out of source
control. JavaScript bundles should not include secrets or private endpoints.
The release bundle guard should fail closed if the app cannot resolve a
JavaScript bundle URL.
The placeholder bundle guard should also fail closed when `main.jsbundle` still
contains the checked-in empty bundle instructions.
The blank bundle guard should fail closed when bundle contents are missing,
empty, or whitespace only.
The bundle module guard should fail closed when a release bundle does not
register the expected `WowNativeReact` module.
The release bundle file URL guard should fail closed when release startup
resolves anything other than a local bundle file.
The exact bundle registration guard should fail closed unless the release
bundle registers the same module that `RCTRootView` launches.
The bundle module name guard should fail closed when the expected module name is
blank or whitespace-only.
The release bundle resource guard should keep `iOS/main.jsbundle` copied into
the app target resources that release startup expects.
Vendored framework integrity checks should detect changes to Fabric,
Crashlytics, and their executable build tools without claiming those legacy
artifacts are trusted or supported.

## What We Will Not Merge (For Now)

- Hardcoded service credentials
- Broad React Native migrations without a plan
- Generated artifacts whose ownership is unclear
- Build changes that make the sample unrecoverable

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
