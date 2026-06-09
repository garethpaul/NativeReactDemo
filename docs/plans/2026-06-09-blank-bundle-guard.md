# Blank Bundle Guard Plan

status: completed

## Context

Release startup already rejects missing bundle URLs and the checked-in
placeholder `main.jsbundle` instructions before creating `RCTRootView`.
However, an empty or whitespace-only bundled file has the same runtime failure
mode and should also fail closed before React Native startup.

## Objectives

- Treat nil bundle URLs passed to the placeholder helper as unsafe.
- Reject empty or whitespace-only release bundle contents.
- Preserve the existing checked-in placeholder string guard.
- Extend `make check` and docs so blank bundle guard behavior remains visible.

## Verification

- `make check`
- `git diff --check`
