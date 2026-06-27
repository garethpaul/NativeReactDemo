# AGENTS.md

## Repository purpose

`garethpaul/NativeReactDemo` is an Apple platform application or Objective-C/Swift sample. NativeReactDemo

## Project structure

- `Makefile` - repository verification targets
- `scripts` - baseline checks and helper scripts
- `docs` - plans, notes, and generated README assets
- `package.json` - Node package metadata and scripts
- `WowNativeReact.xcodeproj` - Xcode project
- `Crashlytics.framework` - repository source or sample assets
- `Fabric.framework` - repository source or sample assets
- `iOS` - repository source or sample assets
- `WowNativeReactTests` - repository source or sample assets

## Development commands

- Install dependencies: `npm install`
- Full baseline: `make check`
- package script `start`: `npm start`
- package script `check`: `npm run check`
- Local Apple development: `open WowNativeReact.xcodeproj`
- If a command above skips because a platform toolchain is missing, verify on a machine with that SDK before claiming platform behavior is tested.

## Coding conventions

- Language mix noted in the README: C/C++ headers (7), Objective-C (3), JavaScript (1).
- Keep React components controlled and covered by component tests when props or rendering behavior changes.
- Preserve legacy Xcode project settings and signing assumptions unless the change is explicitly about modernization.

## Testing guidance

- Test-related files detected: `docs/plans/2026-06-08-native-react-test-baseline.md`, `WowNativeReactTests/WowNativeReactTests.m`
- Start with the narrowest relevant test or Make target, then run `make check` before handing off if the change is not documentation-only.
- Keep README verification notes in sync when commands, fixtures, or supported toolchains change.

## PR / change guidance

- Keep diffs focused on the requested repository and avoid unrelated modernization or formatting churn.
- Preserve public APIs, sample behavior, file formats, and documented environment variables unless the task explicitly changes them.
- Update tests, README notes, or docs/plans when behavior, security posture, or validation commands change.
- Call out skipped platform validation, legacy toolchain assumptions, and any risky files touched in the final summary.

## Safety and gotchas

- Fabric/Crashlytics credentials, signing material, local xcconfig files, `.env` files, and private endpoints should stay out of git.
- Release builds load `iOS/main.jsbundle`; the checked-in bundle is a placeholder, so regenerate it intentionally when JavaScript changes need to ship without the packager.
- The release bundle guard returns safely during launch if no JavaScript bundle URL is available.
- The placeholder bundle guard also fails closed if release startup resolves the checked-in empty bundle.
- The blank bundle guard treats missing, empty, or whitespace-only release bundle content as an unsafe placeholder.
- The bundle module guard treats release bundles without the expected `WowNativeReact` registration as unsafe.
- Exact module registration checks require the closing quote and following
  argument comma, so names that only start with `WowNativeReact` remain unsafe.
- Release module registration must be executable JavaScript code, not text inside comments, string literals, or regular-expression literals.

## Agent workflow

1. Inspect the README, Makefile, manifests, and the files directly related to the request.
2. Make the smallest source or docs change that satisfies the task; avoid generated, vendored, or local-environment files unless required.
3. Run the narrowest useful validation first, then `make check` or the documented package/platform gate when available.
4. If a required SDK, service credential, or external runtime is unavailable, record the skipped command and why.
5. Summarize changed files, commands run, and remaining risks or follow-up validation.
