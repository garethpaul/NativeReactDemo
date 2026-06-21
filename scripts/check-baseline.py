#!/usr/bin/env python3
"""Static baseline checks for the legacy React Native iOS demo."""

from pathlib import Path
import hashlib
import json
import os
import plistlib
import re
import stat
import subprocess
import sys
from typing import Optional
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
MAXIMUM_TEXT_BYTES = 1024 * 1024
MAXIMUM_PROJECT_BYTES = 2 * 1024 * 1024
MAXIMUM_RELEASE_BUNDLE_BYTES = 10 * 1024 * 1024
MAXIMUM_VENDORED_ARTIFACT_BYTES = 8 * 1024 * 1024
EXPECTED_MAKEFILE = """ifneq ($(origin MAKEFILE_LIST),file)
$(error MAKEFILE_LIST must not be overridden)
endif
override ROOT := $(shell path='$(subst ','"'"',$(MAKEFILE_LIST))'; path=$${path\\# }; dirname -- "$$path")

.PHONY: build check lint static-check test verify

check: test

lint build verify: static-check

test: static-check
\tpython3 -m unittest discover -s "$(ROOT)/tests" -p 'test_*.py'

static-check:
\tpython3 "$(ROOT)/scripts/check-baseline.py"
"""
REQUIRED = [
    ".gitignore",
    ".github/CODEOWNERS",
    ".github/workflows/check.yml",
    "AGENTS.md",
    "Makefile",
    "README.md",
    "SECURITY.md",
    "VISION.md",
    "VENDORED_FRAMEWORKS.sha256",
    "package.json",
    "index.ios.js",
    "iOS/AppDelegate.m",
    "iOS/Info.plist",
    "iOS/main.jsbundle",
    "Fabric.framework/Fabric",
    "Fabric.framework/run",
    "Crashlytics.framework/Crashlytics",
    "Crashlytics.framework/run",
    "Crashlytics.framework/submit",
    "WowNativeReact.xcodeproj/project.pbxproj",
    "WowNativeReactTests/WowNativeReactTests.m",
    "tests/__init__.py",
    "tests/test_check_baseline.py",
    "docs/plans/2026-06-08-native-react-demo-baseline.md",
    "docs/plans/2026-06-08-native-react-test-baseline.md",
    "docs/plans/2026-06-08-placeholder-bundle-guard.md",
    "docs/plans/2026-06-08-release-bundle-guard.md",
    "docs/plans/2026-06-09-blank-bundle-guard.md",
    "docs/plans/2026-06-09-make-gate-aliases.md",
    "docs/plans/2026-06-09-release-bundle-module-guard.md",
    "docs/plans/2026-06-09-release-bundle-file-url-guard.md",
    "docs/plans/2026-06-09-exact-bundle-registration-guard.md",
    "docs/plans/2026-06-09-bundle-module-name-guard.md",
    "docs/plans/2026-06-10-release-bundle-resource-guard.md",
    "docs/plans/2026-06-10-hosted-project-validation.md",
    "docs/plans/2026-06-10-vendored-framework-integrity.md",
    "docs/plans/2026-06-12-release-bundle-size-guard.md",
    "docs/plans/2026-06-12-checkout-credential-boundary.md",
    "docs/plans/2026-06-13-location-independent-make.md",
    "docs/plans/2026-06-14-release-bundle-regular-file-guard.md",
    "docs/plans/2026-06-15-release-placeholder-shape-guard.md",
    "docs/plans/2026-06-19-native-react-deep-review.md",
]

VENDORED_EXECUTABLES = {
    "Fabric.framework/Fabric",
    "Fabric.framework/run",
    "Crashlytics.framework/Crashlytics",
    "Crashlytics.framework/run",
    "Crashlytics.framework/submit",
}


class ValidationError(ValueError):
    pass


def regular_file_size(path: Path, maximum_bytes: int) -> int:
    try:
        metadata = path.lstat()
    except OSError as error:
        raise ValidationError(f"could not inspect {path}: {error}") from error
    if not stat.S_ISREG(metadata.st_mode):
        raise ValidationError(f"expected regular file: {path}")
    if metadata.st_size > maximum_bytes:
        raise ValidationError(
            f"file exceeds {maximum_bytes} byte limit: {path} ({metadata.st_size} bytes)"
        )
    return metadata.st_size


def open_regular_file(path: Path, maximum_bytes: int) -> int:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as error:
        raise ValidationError(f"could not open regular file {path}: {error}") from error
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode):
            raise ValidationError(f"expected regular file: {path}")
        if metadata.st_size > maximum_bytes:
            raise ValidationError(
                f"file exceeds {maximum_bytes} byte limit: {path} ({metadata.st_size} bytes)"
            )
    except Exception:
        os.close(descriptor)
        raise
    return descriptor


def read_bytes_file(path: Path, maximum_bytes: int) -> bytes:
    descriptor = open_regular_file(path, maximum_bytes)
    chunks = []
    total = 0
    try:
        while True:
            chunk = os.read(descriptor, min(64 * 1024, maximum_bytes + 1 - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            if total > maximum_bytes:
                raise ValidationError(f"file grew beyond {maximum_bytes} byte limit: {path}")
    finally:
        os.close(descriptor)
    return b"".join(chunks)


def read_text_file(path: Path, maximum_bytes: int) -> str:
    return read_bytes_file(path, maximum_bytes).decode("utf-8", errors="replace")


def sha256_regular_file(path: Path, maximum_bytes: int) -> str:
    descriptor = open_regular_file(path, maximum_bytes)
    digest = hashlib.sha256()
    total = 0
    try:
        while True:
            chunk = os.read(descriptor, 64 * 1024)
            if not chunk:
                break
            total += len(chunk)
            if total > maximum_bytes:
                raise ValidationError(f"file grew beyond {maximum_bytes} byte limit: {path}")
            digest.update(chunk)
    finally:
        os.close(descriptor)
    return digest.hexdigest()


def project_bundle_reference_errors(project: str) -> list[str]:
    bundle_paths = re.findall(
        r"\bpath\s*=\s*\"?([^\";]*\.jsbundle)\"?;", project, flags=re.IGNORECASE
    )
    errors = []
    if bundle_paths != ["iOS/main.jsbundle"]:
        errors.append("Xcode project must reference exactly iOS/main.jsbundle")
    if "main.jsbundle in Resources" not in project:
        errors.append("Xcode project must copy iOS/main.jsbundle into app resources")
    return errors


def workflow_policy_errors(workflow: str) -> list[str]:
    errors = []
    if workflow.count("permissions:") != 1 or "permissions:\n  contents: read" not in workflow:
        errors.append("workflow must keep one repository-level read-only permission boundary")
    if "${{ secrets." in workflow:
        errors.append("workflow must not reference repository secrets")
    if "persist-credentials: true" in workflow or "persist-credentials: false" not in workflow:
        errors.append("workflow checkout must disable persisted credentials")
    for action_reference in re.findall(r"uses:\s+([^\s]+)", workflow):
        if action_reference.startswith("./"):
            continue
        if re.fullmatch(r"[^@\s]+@[0-9a-f]{40}", action_reference) is None:
            errors.append(f"workflow action must use a full commit pin: {action_reference}")
    return errors


def resolve_xcodebuild() -> Optional[Path]:
    xcrun = Path("/usr/bin/xcrun")
    if not xcrun.is_file():
        return None
    result = subprocess.run(
        [str(xcrun), "--find", "xcodebuild"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    candidate = Path(result.stdout.strip())
    if not candidate.is_absolute() or not candidate.is_file():
        return None
    return candidate


def read(path: str) -> str:
    maximum_bytes = MAXIMUM_TEXT_BYTES
    if path == "WowNativeReact.xcodeproj/project.pbxproj":
        maximum_bytes = MAXIMUM_PROJECT_BYTES
    elif path == "iOS/main.jsbundle":
        maximum_bytes = MAXIMUM_RELEASE_BUNDLE_BYTES
    return read_text_file(ROOT / path, maximum_bytes)


def main() -> int:
    failures = []
    for path in REQUIRED:
        maximum_bytes = MAXIMUM_TEXT_BYTES
        if path == "WowNativeReact.xcodeproj/project.pbxproj":
            maximum_bytes = MAXIMUM_PROJECT_BYTES
        elif path == "iOS/main.jsbundle":
            maximum_bytes = MAXIMUM_RELEASE_BUNDLE_BYTES
        elif path in VENDORED_EXECUTABLES:
            maximum_bytes = MAXIMUM_VENDORED_ARTIFACT_BYTES
        try:
            regular_file_size(ROOT / path, maximum_bytes)
        except ValidationError:
            failures.append(f"required file missing: {path}")

    package = json.loads(read("package.json"))
    makefile = read("Makefile")
    if makefile != EXPECTED_MAKEFILE:
        failures.append("Makefile must exactly preserve rooted SDK-free aliases")

    if package.get("dependencies", {}).get("react-native") != "0.4.2":
        failures.append("react-native dependency must stay pinned to 0.4.2")
    if package.get("scripts", {}).get("check") != "python3 scripts/check-baseline.py":
        failures.append("package.json must expose npm run check")

    manifest_entries = {}
    for line_number, line in enumerate(read("VENDORED_FRAMEWORKS.sha256").splitlines(), 1):
        parts = line.split("  ", 1)
        if len(parts) != 2 or re.fullmatch(r"[0-9a-f]{64}", parts[0]) is None or not parts[1]:
            failures.append(f"VENDORED_FRAMEWORKS.sha256 line {line_number} is malformed")
            continue
        digest, relative_path = parts
        if relative_path in manifest_entries:
            failures.append(f"VENDORED_FRAMEWORKS.sha256 duplicates {relative_path}")
            continue
        manifest_entries[relative_path] = digest
    if set(manifest_entries) != VENDORED_EXECUTABLES:
        failures.append("VENDORED_FRAMEWORKS.sha256 must list exactly the vendored executable artifacts")
    for relative_path in VENDORED_EXECUTABLES:
        path = ROOT / relative_path
        if relative_path not in manifest_entries:
            continue
        try:
            actual_digest = sha256_regular_file(path, MAXIMUM_VENDORED_ARTIFACT_BYTES)
        except ValidationError as error:
            failures.append(str(error))
            continue
        if actual_digest != manifest_entries[relative_path]:
            failures.append(f"vendored framework integrity mismatch: {relative_path}")

    app_delegate = read("iOS/AppDelegate.m")
    project = read("WowNativeReact.xcodeproj/project.pbxproj")
    if "#if DEBUG" not in app_delegate or "#else" not in app_delegate:
        failures.append("AppDelegate must gate localhost bundle loading to DEBUG builds")
    if 'URLForResource:@"main" withExtension:@"jsbundle"' not in app_delegate:
        failures.append("AppDelegate must load main.jsbundle outside DEBUG")
    if "jsCodeLocation == nil" not in app_delegate or "return NO;" not in app_delegate:
        failures.append("AppDelegate must fail closed when the JavaScript bundle URL is unavailable")
    if "isPlaceholderBundleAtURL:" not in app_delegate or "Offline JS file is empty" not in app_delegate:
        failures.append("AppDelegate must fail closed when release resolves the placeholder JavaScript bundle")
    if (
        "static NSString * const ReleasePlaceholderContents" not in app_delegate
        or "bundleContentsMatchReleasePlaceholder:" not in app_delegate
        or "stringByReplacingOccurrencesOfString:@\"\\r\\n\" withString:@\"\\n\"" not in app_delegate
        or "[normalizedBundleContents isEqualToString:ReleasePlaceholderContents]" not in app_delegate
        or "return [self bundleContentsMatchReleasePlaceholder:bundleContents];" not in app_delegate
        or "hasPrefix:ReleasePlaceholder" in app_delegate
        or "hasSuffix:ReleasePlaceholder" in app_delegate
        or 'rangeOfString:@"Offline JS file is empty"' in app_delegate
    ):
        failures.append("AppDelegate must match the normalized release placeholder exactly")
    if "#ifndef DEBUG" not in app_delegate:
        failures.append("placeholder JavaScript bundle guard must stay outside DEBUG builds")
    if "bundleURL == nil" not in app_delegate:
        failures.append("placeholder bundle helper must fail closed when called with a nil URL")
    if "![bundleURL isFileURL]" not in app_delegate:
        failures.append("placeholder bundle helper must fail closed when release bundle URL is not local")
    size_limit_index = app_delegate.find("MaximumReleaseBundleBytes = 10ULL * 1024ULL * 1024ULL")
    attributes_index = app_delegate.find("attributesOfItemAtPath:[bundleURL path]")
    file_type_index = app_delegate.find("NSString *bundleType = [bundleAttributes objectForKey:NSFileType]")
    regular_file_guard_index = app_delegate.find("![bundleType isEqualToString:NSFileTypeRegular]")
    size_guard_index = app_delegate.find("[bundleSize unsignedLongLongValue] > MaximumReleaseBundleBytes")
    contents_read_index = app_delegate.find("stringWithContentsOfURL:bundleURL")
    if not (
        0 <= size_limit_index < attributes_index < file_type_index
        < regular_file_guard_index < size_guard_index < contents_read_index
    ):
        failures.append("release bundle size guard must fail closed before reading bundle contents")
    if "bundleAttributes == nil || bundleType == nil || bundleSize == nil" not in app_delegate:
        failures.append("release bundle size guard must fail closed when file metadata is unavailable")
    has_blank_bundle_guard = (
        "stringByTrimmingCharactersInSet" in app_delegate
        and "whitespaceAndNewlineCharacterSet" in app_delegate
    )
    if not has_blank_bundle_guard:
        failures.append("placeholder bundle helper must reject blank or whitespace-only bundle contents")
    if "AppRegistry.registerComponent" not in app_delegate or "WowNativeReact" not in app_delegate:
        failures.append("placeholder bundle helper must reject release bundles without the expected module registration")
    if (
        'static NSString * const NativeReactModuleName = @"WowNativeReact";' not in app_delegate
        or "- (BOOL)bundleContents:(NSString *)bundleContents registersModule:(NSString *)moduleName" not in app_delegate
        or "AppRegistry.registerComponent('%@'" not in app_delegate
        or 'AppRegistry.registerComponent(\\"%@\\"' not in app_delegate
        or "[self bundleContents:bundleContents registersModule:NativeReactModuleName]" not in app_delegate
        or "moduleName:NativeReactModuleName" not in app_delegate
    ):
        failures.append("AppDelegate must validate exact React Native bundle module registration")
    if (
        "NSString *trimmedModuleName = [moduleName stringByTrimmingCharactersInSet:" not in app_delegate
        or "trimmedModuleName.length == 0" not in app_delegate
        or 'NSString *singleQuotedRegistration = [NSString stringWithFormat:@"AppRegistry.registerComponent(\'%@\'", trimmedModuleName];' not in app_delegate
        or 'NSString *doubleQuotedRegistration = [NSString stringWithFormat:@"AppRegistry.registerComponent(\\"%@\\"", trimmedModuleName];' not in app_delegate
    ):
        failures.append("AppDelegate must reject blank bundle module names before registration checks")
    failures.extend(project_bundle_reference_errors(project))

    js = read("index.ios.js")
    if re.search(r"http://", js):
        failures.append("index.ios.js must not include insecure HTTP asset URLs")
    tests = read("WowNativeReactTests/WowNativeReactTests.m")
    if 'TEXT_TO_LOOK_FOR @"Hi"' not in tests:
        failures.append("Xcode UI test must look for the text rendered by index.ios.js")
    if "textForView:" not in tests or "@selector(text)" not in tests:
        failures.append("Xcode UI test must handle both attributedText and text views")
    if (
        "testRejectsCheckedInReleasePlaceholder" not in tests
        or "temporaryBundleURLWithContents:" not in tests
        or "writeToURL:bundleURL" not in tests
        or "// $ react-native bundle --minify" not in tests
        or "XCTAssertTrue([delegate bundleContentsMatchReleasePlaceholder:placeholder])" not in tests
        or "XCTAssertTrue([delegate isPlaceholderBundleAtURL:bundleURL])" not in tests
    ):
        failures.append("Xcode tests must reject the checked-in release placeholder shape")
    if (
        "testAcceptsRegisteredBundleContainingPlaceholderMarker" not in tests
        or "AppRegistry.registerComponent('WowNativeReact'" not in tests
        or "var diagnostic = 'Offline JS file is empty'" not in tests
        or "XCTAssertFalse([delegate bundleContentsMatchReleasePlaceholder:bundleContents])" not in tests
        or "XCTAssertFalse([delegate isPlaceholderBundleAtURL:bundleURL])" not in tests
    ):
        failures.append("Xcode tests must accept registered bundles with an unrelated placeholder marker")
    if (
        "testAcceptsRegisteredBundleWithPlaceholderBoundariesAndAdditionalContent" not in tests
        or "XCTAssertFalse([delegate bundleContentsMatchReleasePlaceholder:bundleContents])" not in tests
    ):
        failures.append("Xcode tests must reject broad placeholder boundary matching")

    info = plistlib.loads(read_bytes_file(ROOT / "iOS/Info.plist", MAXIMUM_TEXT_BYTES))
    if info.get("NSLocationWhenInUseUsageDescription") == "":
        failures.append("Info.plist must not contain an empty location usage string")

    gitignore = read(".gitignore")
    for expected in [
        "node_modules/",
        "*.local.xcconfig",
        "*.secrets.xcconfig",
        "*.mobileprovision",
        "*.p12",
        "*.cer",
        "*.p8",
        ".xcode.env.local",
        ".env",
    ]:
        if expected not in gitignore:
            failures.append(f".gitignore must include {expected}")

    for xml_path in ["docs/readme-overview.svg", "iOS/Base.lproj/LaunchScreen.xib"]:
        try:
            ET.fromstring(read_bytes_file(ROOT / xml_path, MAXIMUM_TEXT_BYTES))
        except Exception as error:
            failures.append(f"{xml_path} must parse as XML: {error}")

    readme = read("README.md")
    docs = readme + "\n" + read("VISION.md") + "\n" + read("SECURITY.md")
    changes = read("CHANGES.md")
    location_independent_make_plan = read(
        "docs/plans/2026-06-13-location-independent-make.md"
    )
    if "make -f /path/to/NativeReactDemo/Makefile check" not in readme:
        failures.append("README must document location-independent Makefile invocation")
    if not all(
        evidence in location_independent_make_plan.lower()
        for evidence in [
            "status: completed",
            "root and external-directory",
            "five isolated hostile mutations",
        ]
    ):
        failures.append(
            "location-independent Make plan must record completed root, external, and mutation verification"
        )
    for phrase in ["make lint", "make test", "make build", "make check", "Fabric/Crashlytics", "main.jsbundle"]:
        if phrase not in docs:
            failures.append(f"docs must mention {phrase}")
    if "release bundle guard" not in docs:
        failures.append("docs must mention release bundle guard handling")
    if "placeholder bundle guard" not in docs:
        failures.append("docs must mention placeholder bundle guard handling")
    if "blank bundle guard" not in docs:
        failures.append("docs must mention blank bundle guard handling")
    if "bundle module guard" not in docs:
        failures.append("docs must mention bundle module guard handling")
    if "release bundle file URL guard" not in docs:
        failures.append("docs must mention release bundle file URL guard handling")
    if "exact bundle registration guard" not in docs:
        failures.append("docs must mention exact bundle registration guard handling")
    if "bundle module name guard" not in docs:
        failures.append("docs must mention bundle module name guard handling")
    if "release bundle resource guard" not in docs:
        failures.append("docs must mention release bundle resource guard handling")
    if "release bundle size guard" not in docs:
        failures.append("docs must mention release bundle size guard handling")
    for relative_path in ["README.md", "SECURITY.md", "VISION.md"]:
        if "release bundle regular-file guard" not in read(relative_path):
            failures.append(f"{relative_path} must mention release bundle regular-file guard handling")
        if "release placeholder shape guard" not in read(relative_path):
            failures.append(f"{relative_path} must mention release placeholder shape guard handling")
    if "vendored framework integrity" not in docs.lower():
        failures.append("docs must mention vendored framework integrity handling")
    if "placeholder bundle guard" not in changes:
        failures.append("CHANGES must mention placeholder bundle guard handling")
    if "blank bundle guard" not in changes:
        failures.append("CHANGES must mention blank bundle guard handling")
    if "bundle module guard" not in changes:
        failures.append("CHANGES must mention bundle module guard handling")
    if "release bundle file URL guard" not in changes:
        failures.append("CHANGES must mention release bundle file URL guard handling")
    if "exact bundle registration guard" not in changes:
        failures.append("CHANGES must mention exact bundle registration guard handling")
    if "bundle module name guard" not in changes:
        failures.append("CHANGES must mention bundle module name guard handling")
    if "release bundle resource guard" not in changes:
        failures.append("CHANGES must mention release bundle resource guard handling")
    if "release bundle regular-file guard" not in changes:
        failures.append("CHANGES must mention release bundle regular-file guard handling")
    if "release placeholder shape guard" not in changes:
        failures.append("CHANGES must mention release placeholder shape guard handling")
    if "vendored framework integrity" not in changes.lower():
        failures.append("CHANGES must mention vendored framework integrity handling")
    if "make lint" not in changes or "make test" not in changes or "make build" not in changes or "make check" not in changes:
        failures.append("CHANGES must mention standard Make gate aliases")
    if "Offline JS file is empty" in read("iOS/main.jsbundle") and "placeholder" not in read("README.md"):
        failures.append("README must document the checked-in main.jsbundle placeholder")

    placeholder_shape_plan = read("docs/plans/2026-06-15-release-placeholder-shape-guard.md")
    if not all(
        evidence in placeholder_shape_plan.lower()
        for evidence in [
            "status: completed",
            "root and external-directory",
            "seven isolated hostile mutations",
        ]
    ):
        failures.append(
            "release placeholder shape plan must record completed root, external, and mutation verification"
        )

    release_plan = read("docs/plans/2026-06-08-release-bundle-guard.md")
    if "status: completed" not in release_plan:
        failures.append("release bundle guard plan must be marked completed")
    placeholder_plan_path = ROOT / "docs/plans/2026-06-08-placeholder-bundle-guard.md"
    placeholder_plan = placeholder_plan_path.read_text(encoding="utf-8") if placeholder_plan_path.exists() else ""
    if "status: completed" not in placeholder_plan:
        failures.append("placeholder bundle guard plan must be marked completed")
    blank_plan_path = ROOT / "docs/plans/2026-06-09-blank-bundle-guard.md"
    blank_plan = blank_plan_path.read_text(encoding="utf-8") if blank_plan_path.exists() else ""
    if "status: completed" not in blank_plan:
        failures.append("blank bundle guard plan must be marked completed")
    module_plan_path = ROOT / "docs/plans/2026-06-09-release-bundle-module-guard.md"
    module_plan = module_plan_path.read_text(encoding="utf-8") if module_plan_path.exists() else ""
    if "status: completed" not in module_plan:
        failures.append("bundle module guard plan must be marked completed")
    file_url_plan_path = ROOT / "docs/plans/2026-06-09-release-bundle-file-url-guard.md"
    file_url_plan = file_url_plan_path.read_text(encoding="utf-8") if file_url_plan_path.exists() else ""
    if "status: completed" not in file_url_plan:
        failures.append("release bundle file URL guard plan must be marked completed")
    registration_plan_path = ROOT / "docs/plans/2026-06-09-exact-bundle-registration-guard.md"
    registration_plan = registration_plan_path.read_text(encoding="utf-8") if registration_plan_path.exists() else ""
    if "status: completed" not in registration_plan:
        failures.append("exact bundle registration guard plan must be marked completed")
    module_name_plan_path = ROOT / "docs/plans/2026-06-09-bundle-module-name-guard.md"
    module_name_plan = module_name_plan_path.read_text(encoding="utf-8") if module_name_plan_path.exists() else ""
    if "status: completed" not in module_name_plan:
        failures.append("bundle module name guard plan must be marked completed")
    make_gate_plan_path = ROOT / "docs/plans/2026-06-09-make-gate-aliases.md"
    make_gate_plan = make_gate_plan_path.read_text(encoding="utf-8") if make_gate_plan_path.exists() else ""
    if "status: completed" not in make_gate_plan:
        failures.append("Make gate alias plan must be marked completed")
    resource_plan_path = ROOT / "docs/plans/2026-06-10-release-bundle-resource-guard.md"
    resource_plan = resource_plan_path.read_text(encoding="utf-8") if resource_plan_path.exists() else ""
    if "status: completed" not in resource_plan:
        failures.append("release bundle resource guard plan must be marked completed")
    size_plan = read("docs/plans/2026-06-12-release-bundle-size-guard.md")
    if "status: completed" not in size_plan or "hostile mutations" not in size_plan:
        failures.append("release bundle size guard plan must record completed verification")
    regular_file_plan = read("docs/plans/2026-06-14-release-bundle-regular-file-guard.md")
    if "status: completed" not in regular_file_plan or "hostile mutations" not in regular_file_plan:
        failures.append("release bundle regular-file guard plan must record completed verification")
    integrity_plan = read("docs/plans/2026-06-10-vendored-framework-integrity.md")
    if "status: completed" not in integrity_plan or "VENDORED_FRAMEWORKS.sha256" not in integrity_plan:
        failures.append("vendored framework integrity plan must be completed and name the manifest")

    hosted_plan = read("docs/plans/2026-06-10-hosted-project-validation.md")
    workflow = read(".github/workflows/check.yml")
    codeowners = read(".github/CODEOWNERS")
    if codeowners != "* @garethpaul\n":
        failures.append("CODEOWNERS must preserve repository-wide owner review")
    if "status: completed" not in hosted_plan or "make check" not in hosted_plan:
        failures.append("hosted project validation plan must be marked completed")
    for expected in [
        "permissions:\n  contents: read",
        "cancel-in-progress: true",
        "runs-on: macos-15",
        "timeout-minutes: 10",
        "actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10",
        "run: make check",
    ]:
        if expected not in workflow:
            failures.append(f"Check workflow must keep {expected}")

    checkout_plan = read("docs/plans/2026-06-12-checkout-credential-boundary.md")
    if (
        "status: completed" not in checkout_plan
        or "persist-credentials: false" not in checkout_plan
        or "hostile mutations rejected" not in checkout_plan
    ):
        failures.append("checkout credential plan must record completed verification")
    workflow_files = sorted(
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / ".github/workflows").iterdir()
        if path.is_file()
    )
    if workflow_files != [".github/workflows/check.yml"]:
        failures.append("workflow inventory must contain only .github/workflows/check.yml")
    checkout_step = (
        "      - uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10\n"
        "        with:\n"
        "          persist-credentials: false"
    )
    if workflow.count("actions/checkout@") != 1 or checkout_step not in workflow:
        failures.append("Check workflow must keep one pinned credential-free checkout step")
    failures.extend(workflow_policy_errors(workflow))

    guidance = " ".join(
        "\n".join(read(path) for path in ["README.md", "SECURITY.md", "VISION.md", "CHANGES.md"]).split()
    ).lower()
    for phrase in ["checkout credentials are not persisted", "credential-free checkout"]:
        if phrase not in guidance:
            failures.append(f"repository guidance must mention {phrase}")

    xcodebuild = resolve_xcodebuild()
    if xcodebuild is not None:
        result = subprocess.run(
            [str(xcodebuild), "-list", "-project", "WowNativeReact.xcodeproj"],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            failures.append("xcodebuild could not parse WowNativeReact.xcodeproj: " + result.stderr.strip())
    else:
        print("xcodebuild unavailable; static iOS baseline only.")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("NativeReactDemo baseline checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
