# Portable Verification Gates

## Problem

The documented absolute `make -f` command split checkout paths on whitespace,
and the Xcode resolver unit test returned early on hosts without
`/usr/bin/xcrun` before its mocked subprocess boundary was exercised.

## Change

- Derive the repository root from the raw, shell-quoted Makefile path after
  removing GNU Make's leading list separator.
- Reject command-line or environment replacement of GNU Make's automatic
  `MAKEFILE_LIST` value.
- Mock the filesystem boundary in the Xcode resolver test so it remains a unit
  test on Linux while still asserting the absolute `/usr/bin/xcrun` command.
- Cover absolute Makefile paths containing spaces and a literal apostrophe.

## Validation

- Run all Make aliases from the repository and through an absolute Makefile
  path in a hostile checkout name.
- Run the Python test suite and static baseline on Linux.
- Confirm hosted macOS validation still parses the Xcode project.
