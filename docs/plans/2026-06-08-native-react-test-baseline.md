# Native React XCTest Baseline Plan

status: completed

## Context

`NativeReactDemo` includes a legacy XCTest smoke test that waits for the React
Native screen to render the text `Hi`.

## Risk

The test only checked views that respond to `attributedText`. UIKit and older
React Native text wrappers can expose plain `text` instead, which makes the
smoke test brittle even when the expected label is present.

## Work Completed

- Added a `textForView:` helper that reads either `attributedText` or `text`.
- Kept the recursive view search and existing `Hi` assertion behavior.
- Extended `scripts/check-baseline.py` so the broader text helper remains part
  of the host-portable verification path.

## Verification

- `make check`
- `git diff --check`
