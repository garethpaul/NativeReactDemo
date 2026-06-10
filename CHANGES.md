# Changes

## 2026-06-10

- Added a release bundle resource guard so the static baseline catches Xcode
  project changes that stop packaging `iOS/main.jsbundle`.

## 2026-06-08

- Added `make lint`, `make test`, and `make build` aliases so the standard
  gate commands run the same SDK-free static baseline as `make check`.
- Added a bundle module guard so release startup fails closed when a bundle does
  not register `WowNativeReact`.
- Added a release bundle file URL guard so release startup fails closed on
  non-local JavaScript bundle URLs.
- Added an exact bundle registration guard so release startup requires
  `AppRegistry.registerComponent` to register the launched module name.
- Added a bundle module name guard so registration checks fail closed when the
  expected module name is blank.
- Added `make check` and `npm run check` static verification for the legacy React Native iOS sample.
- Pinned the React Native dependency to `0.4.2` for reproducible legacy installs.
- Gated localhost packager bundle loading to debug builds and kept release builds pointed at `main.jsbundle`.
- Added a release bundle guard before creating the React Native root view.
- Added a placeholder bundle guard so release startup fails closed when `main.jsbundle` is still the checked-in placeholder.
- Added a blank bundle guard so release startup fails closed on missing, empty, or whitespace-only bundle contents.
- Removed an unused insecure HTTP image URL from the JavaScript sample.
- Removed the empty location usage string and added local secret/config ignore rules.
- Aligned the Xcode UI test with the rendered `Hi` text.
- Broadened the Xcode UI test to recognize both attributed and plain text views.
- Documented Fabric/Crashlytics credential handling and release bundle ownership.
