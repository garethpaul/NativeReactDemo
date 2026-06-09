# NativeReactDemo Make Gate Aliases

status: completed

## Context

The repository had a single `make check` target for the SDK-free static
baseline. The fleet pre-push sequence also invokes `make lint`, `make test`,
and `make build`, so those commands should reach the same baseline instead of
failing before validation runs.

## Objectives

- Expose lint, test, build, check, and verify Make targets.
- Keep all Make gates delegated to `scripts/check-baseline.py`.
- Document the standard gate commands in README, VISION, SECURITY, and CHANGES.
- Extend the static checker so the Make target contract remains covered.

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- `make verify`
- `git diff --check`
