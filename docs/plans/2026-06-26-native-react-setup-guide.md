# NativeReactDemo Setup Guide Plan

**Goal:** Document NativeReactDemo's legacy compatibility baseline, debug packager, release placeholder, simulator launch, and verification boundaries from checked-in source.

**Architecture:** Preserve React Native 0.4.2, the Objective-C app and tests, checked-in placeholder bundle, vendored frameworks, project settings, and SDK-free validation. Add fail-closed documentation contracts and retire only the completed setup and manual-launch roadmap items.

**Tech Stack:** Markdown, Python 3, Objective-C, React Native 0.4.2, Xcode, GNU Make, GitHub Actions

## Status: Completed

1. Add a failing documentation contract to `scripts/check-baseline.py`.
2. Document legacy compatibility, debug/release launch, and manual simulator checks.
3. Reject isolated hostile mutations for each new guide, roadmap, history, and plan invariant.
4. Run root and external-directory `make check`.
5. Record exact hosted and review evidence before merge.

## Results

- The initial checker failed on the missing guide and passed after reconciliation.
- All 15 final hostile setup-guide mutations were rejected. Preliminary harness
  runs exposed duplicate version/command evidence and one wrapped fixture; the
  contracts were narrowed to unique source-backed sentences before the passing run.
- Root and external-directory `/usr/bin/make check` each passed 42 Make
  authority cases and 14 Python tests; Xcode was unavailable and skipped.
- Live launch remains an isolated legacy macOS/Xcode/Node boundary.
