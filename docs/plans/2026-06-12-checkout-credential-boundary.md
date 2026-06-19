# Checkout Credential Boundary

status: completed

## Context

The hosted macOS gate performs no authenticated Git operation after checkout,
but the action default still retained the read-only workflow token in the
runner's Git configuration.

## Implementation

- Set `persist-credentials: false` on the single commit-pinned checkout step.
- Require exactly one checkout action and only the canonical workflow file.
- Preserve the macOS 15 runner, read-only permission, timeout, concurrency, and
  `make check` command.
- Clarify the distinction between absent service credentials and the checkout
  token in repository guidance.

## Verification

- `make lint`, `make test`, `make build`, and `make check` passed.
- The checker passed from an external working directory.
- Workflow YAML parsing, Python compilation, and `git diff --check` passed.
- Focused hostile mutations rejected a missing or true credential setting,
  duplicate checkout action, extra workflow file, incomplete plan, and stale
  documentation; all hostile mutations rejected.
- Exact-head hosted verification remains pending until this successor is
  pushed.

## Boundaries

- Do not add post-checkout pushes, tags, or authenticated Git fetches.
- Do not run npm install, vendored scripts, builds, signing, or simulators in
  this static hosted gate.
