#!/usr/bin/env python3
"""Static baseline checks for the legacy React Native iOS demo."""

from pathlib import Path
import json
import plistlib
import re
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    ".gitignore",
    "Makefile",
    "README.md",
    "SECURITY.md",
    "VISION.md",
    "package.json",
    "index.ios.js",
    "iOS/AppDelegate.m",
    "iOS/Info.plist",
    "iOS/main.jsbundle",
    "WowNativeReact.xcodeproj/project.pbxproj",
    "WowNativeReactTests/WowNativeReactTests.m",
    "docs/plans/2026-06-08-native-react-demo-baseline.md",
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8", errors="replace")


def main() -> int:
    failures = []
    for path in REQUIRED:
        if not (ROOT / path).is_file():
            failures.append(f"required file missing: {path}")

    package = json.loads(read("package.json"))
    if package.get("dependencies", {}).get("react-native") != "0.4.2":
        failures.append("react-native dependency must stay pinned to 0.4.2")
    if package.get("scripts", {}).get("check") != "python3 scripts/check-baseline.py":
        failures.append("package.json must expose npm run check")

    app_delegate = read("iOS/AppDelegate.m")
    if "#if DEBUG" not in app_delegate or "#else" not in app_delegate:
        failures.append("AppDelegate must gate localhost bundle loading to DEBUG builds")
    if 'URLForResource:@"main" withExtension:@"jsbundle"' not in app_delegate:
        failures.append("AppDelegate must load main.jsbundle outside DEBUG")

    js = read("index.ios.js")
    if re.search(r"http://", js):
        failures.append("index.ios.js must not include insecure HTTP asset URLs")
    tests = read("WowNativeReactTests/WowNativeReactTests.m")
    if 'TEXT_TO_LOOK_FOR @"Hi"' not in tests:
        failures.append("Xcode UI test must look for the text rendered by index.ios.js")
    if "textForView:" not in tests or "@selector(text)" not in tests:
        failures.append("Xcode UI test must handle both attributedText and text views")

    info = plistlib.loads((ROOT / "iOS/Info.plist").read_bytes())
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
            ET.parse(ROOT / xml_path)
        except Exception as error:
            failures.append(f"{xml_path} must parse as XML: {error}")

    docs = read("README.md") + "\n" + read("VISION.md") + "\n" + read("SECURITY.md")
    for phrase in ["make check", "Fabric/Crashlytics", "main.jsbundle"]:
        if phrase not in docs:
            failures.append(f"docs must mention {phrase}")
    if "Offline JS file is empty" in read("iOS/main.jsbundle") and "placeholder" not in read("README.md"):
        failures.append("README must document the checked-in main.jsbundle placeholder")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("NativeReactDemo baseline checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
