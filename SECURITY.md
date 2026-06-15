# Security Policy

## Supported Versions

The supported security scope for `NativeReactDemo` is the current default branch, `master`. Older commits, tags, branches, forks, demos, and generated artifacts are not actively supported unless the repository explicitly marks them as maintained.

Project summary: NativeReactDemo

## Reporting a Vulnerability

Please report suspected vulnerabilities through GitHub's private vulnerability reporting or by opening a draft GitHub Security Advisory for `garethpaul/NativeReactDemo` when that option is available. If GitHub does not show a private reporting option for this repository, contact the repository owner through GitHub and avoid posting exploit details publicly until the issue can be assessed.

Do not open a public issue that includes exploit code, secrets, personal data, or detailed reproduction steps for an unpatched vulnerability.

## What to Include

Helpful reports include:

- the affected file, endpoint, permission, dependency, or workflow
- a concise impact statement explaining what an attacker could do
- reproduction steps using test data and accounts you control
- the branch, commit SHA, platform version, device, runtime, or dependency versions used
- logs, screenshots, or proof-of-concept snippets that demonstrate impact without exposing private data

## Project Security Posture

- This repository appears to be an Apple platform application or Swift sample. The active security scope is the code and documentation on the default branch.
- Review found authentication, token, or session-related code paths; changes in those areas should receive security-focused review before merge.
- Review found external API integrations or credential-adjacent configuration; changes in those areas should receive security-focused review before merge.
- Review found network clients, sockets, web APIs, or service endpoints; changes in those areas should receive security-focused review before merge.
- Review found mobile permission or privacy-sensitive data handling; changes in those areas should receive security-focused review before merge.
- Review found file, document, data, or media parsing flows; changes in those areas should receive security-focused review before merge.
- Dependency manifests detected: package.json. Dependency updates should preserve lockfiles when present and avoid introducing packages without a clear maintenance reason.
- Run `make lint`, `make test`, `make build`, and `make check` after changing JavaScript, plist files, Xcode project metadata, Fabric/Crashlytics setup, or security docs.
- The pinned macOS workflow runs only static checks and project parsing without
  npm install, service credentials, vendored script execution, build, signing,
  simulator launch, or application execution.
- The hosted gate uses a credential-free checkout so its read-only token is not
  retained in the runner's Git configuration.
- Fabric/Crashlytics credentials, signing material, local xcconfig files, `.env` files, and private endpoints should stay out of git.
- Vendored framework integrity is checked against
  `VENDORED_FRAMEWORKS.sha256`; matching hashes detect replacement but do not
  establish provenance, support status, or safety of these legacy binaries.
- Release builds should use the checked-in `main.jsbundle` intentionally, while localhost packager loading should remain DEBUG-only.
- The release bundle guard should fail closed if startup cannot resolve a JavaScript bundle URL.
- The placeholder bundle guard should fail closed if release startup resolves the checked-in empty JavaScript bundle.
- The blank bundle guard should fail closed if release startup resolves missing, empty, or whitespace-only JavaScript bundle content.
- The bundle module guard should fail closed if release startup resolves JavaScript that does not register `WowNativeReact`.
- The release bundle file URL guard should fail closed if release startup
  resolves anything other than a local JavaScript bundle file.
- The exact bundle registration guard should fail closed unless release
  JavaScript registers the same module name used for `RCTRootView` startup.
- The bundle module name guard should fail closed before registration checks if
  the expected React Native module name is blank or whitespace-only.
- The release bundle resource guard should keep `iOS/main.jsbundle` in the app
  target resources so release startup does not depend on a missing bundle.
- The release bundle size guard should reject missing file metadata and local
  JavaScript bundles larger than 10 MiB before reading their contents.
- The release bundle regular-file guard should reject symbolic links and other
  non-regular resources before trusting size metadata or reading contents.
- The release placeholder shape guard should require both checked-in content
  boundaries instead of rejecting valid bundles that merely mention the
  placeholder error text.

## Mobile Privacy Notes

If this project requests device permissions such as location, camera, microphone, contacts, Bluetooth, health data, or local storage access, reports should describe the permission involved and whether sensitive data can be accessed, persisted, or transmitted unexpectedly. Please avoid testing against real third-party user data or accounts you do not control.

For this app, bundle-loading reports should include whether the release bundle
guard prevents nil JavaScript bundle URLs from reaching `RCTRootView`, and
whether the placeholder bundle guard rejects the checked-in empty bundle.
Reports should also note whether the blank bundle guard rejects missing, empty,
or whitespace-only bundle content before `RCTRootView` startup.
Reports should also note whether the bundle module guard rejects malformed
release JavaScript before `RCTRootView` startup.
Reports should also note whether the release bundle file URL guard rejects
non-local JavaScript bundle URLs before `RCTRootView` startup.
Reports should also note whether the exact bundle registration guard rejects
malformed JavaScript that only mentions the module name without registering it.
Reports should also note whether the bundle module name guard rejects blank or
whitespace-only expected module names before release bundle registration checks.
Reports should also note whether the release bundle resource guard catches
project changes that stop packaging `iOS/main.jsbundle`.

## Dependency and Supply Chain Security

Dependency updates should come from trusted package managers and should keep lockfiles in sync when lockfiles exist. Do not commit credentials, private keys, tokens, generated secrets, signing material, private endpoints, or machine-local configuration. If a vulnerability depends on a compromised package, typosquatting risk, insecure transitive dependency, or unsafe build step, include the package name, affected version, and the path through which it is used.

## Safe Research Guidelines

Good-faith research is welcome when it stays within these boundaries:

- use only accounts, devices, data, and infrastructure that you own or have explicit permission to test
- avoid destructive actions, persistence, spam, phishing, social engineering, or denial-of-service testing
- minimize access to personal data and stop testing immediately if private data is exposed
- do not exfiltrate secrets or third-party data; report the minimum evidence needed to verify impact
- keep vulnerability details confidential until the maintainer has assessed the report

## Maintainer Response

The maintainer will review complete reports as availability allows, prioritize issues by exploitability and impact, and coordinate a fix or mitigation when the affected code is still maintained. For sample, archived, or educational repositories, the likely remediation may be documentation, dependency updates, or clearly marking unsupported code rather than a production-style patch release.
