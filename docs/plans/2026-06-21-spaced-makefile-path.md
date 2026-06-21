# Spaced Absolute Makefile Path Verification

status: completed

## Context

GNU Make list functions split a loaded absolute Makefile path at spaces. A
checkout path containing spaces, brackets, and an apostrophe therefore sent
the SDK-free baseline and test discovery to a fabricated caller path.

## Scope

1. Derive the checkout root from the complete `MAKEFILE_LIST` value.
2. Preserve the authoritative root against command-line and environment input.
3. Reject command-line or environment-preferred `MAKEFILE_LIST` overrides.
4. Exercise all six Make aliases from an external working directory.

## Verification

- Root and external hostile-path gates passed on Python 3.12 and 3.14.
- All six Make aliases retained the checkout with no override and with
  command-line or environment `ROOT` input.
- Both tested `MAKEFILE_LIST` override paths failed closed.
- The SDK-free suite passed 16 tests; npm validation and diff checks passed.

## Risk And Rollback

This changes SDK-free verification root discovery only. Rollback restores the
previous root expression and removes the three hostile-path tests.
