## Native React Demo Vision

This document explains the current state and direction of the project.
Project overview and developer docs: [`README.md`](README.md)

Native React Demo is an early React Native iOS sample with a bundled iOS app,
React Native 0.4-era JavaScript, and Fabric/Crashlytics frameworks.

The repository is useful as a preserved example of early React Native project
layout and iOS integration. Project context lives in [`README.md`](README.md).

The goal is to keep the demo understandable while making legacy dependency and
credential assumptions clear.

The current focus is:

Priority:

- Preserve the React Native iOS bridge and app structure
- Keep `npm start` and package metadata visible for the old toolchain
- Avoid committing Fabric/Crashlytics credentials or signing material
- Maintain security policy for the sample

Next priorities:

- Add README setup and supported Node/Xcode notes
- Modernize React Native only in a dedicated migration
- Add a simple verification path for launching the iOS app
- Clarify whether generated bundles should remain checked in

Contribution rules:

- One PR = one focused React Native, iOS, dependency, or documentation change.
- Keep credentials and generated signing files out of git.
- Verify the app after bridge or bundle changes.
- Do not mix React Native major migrations with app behavior changes.

## Security

Canonical security policy and reporting:

- [`SECURITY.md`](SECURITY.md)

Crash-reporting credentials and signing material must remain out of source
control. JavaScript bundles should not include secrets or private endpoints.

## What We Will Not Merge (For Now)

- Hardcoded service credentials
- Broad React Native migrations without a plan
- Generated artifacts whose ownership is unclear
- Build changes that make the sample unrecoverable

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
