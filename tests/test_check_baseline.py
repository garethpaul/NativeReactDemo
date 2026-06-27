import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "check_baseline", ROOT / "scripts" / "check-baseline.py"
)
check_baseline = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(check_baseline)


class MakefileRootTests(unittest.TestCase):
    def test_make_authority_harness(self):
        result = subprocess.run(
            ["/bin/sh", str(ROOT / "scripts" / "test-makefile-root.sh")],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("42 target/authority cases", result.stdout)


class BoundedFileTests(unittest.TestCase):
    def test_read_text_rejects_symlink(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target.txt"
            target.write_text("safe", encoding="utf-8")
            link = root / "link.txt"
            link.symlink_to(target)

            with self.assertRaises(check_baseline.ValidationError):
                check_baseline.read_text_file(link, maximum_bytes=16)

    def test_read_text_rejects_oversize_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "large.txt"
            path.write_bytes(b"x" * 17)

            with self.assertRaises(check_baseline.ValidationError):
                check_baseline.read_text_file(path, maximum_bytes=16)

    def test_hash_rejects_symlink(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target.bin"
            target.write_bytes(b"binary")
            link = root / "link.bin"
            link.symlink_to(target)

            with self.assertRaises(check_baseline.ValidationError):
                check_baseline.sha256_regular_file(link, maximum_bytes=64)


class ProjectReferenceTests(unittest.TestCase):
    def test_accepts_one_canonical_release_bundle_reference(self):
        project = "path = iOS/main.jsbundle;\nmain.jsbundle in Resources"
        self.assertEqual(check_baseline.project_bundle_reference_errors(project), [])

    def test_rejects_case_variant_release_bundle_reference(self):
        project = "path = iOS/Main.jsbundle;\nmain.jsbundle in Resources"
        self.assertNotEqual(check_baseline.project_bundle_reference_errors(project), [])

    def test_rejects_traversal_release_bundle_reference(self):
        project = "path = iOS/../iOS/main.jsbundle;\nmain.jsbundle in Resources"
        self.assertNotEqual(check_baseline.project_bundle_reference_errors(project), [])

    def test_rejects_duplicate_release_bundle_reference(self):
        project = (
            "path = iOS/main.jsbundle;\n"
            "path = iOS/main.jsbundle;\n"
            "main.jsbundle in Resources"
        )
        self.assertNotEqual(check_baseline.project_bundle_reference_errors(project), [])


class WorkflowPolicyTests(unittest.TestCase):
    def setUp(self):
        self.workflow = """name: Check
permissions:
  contents: read
jobs:
  baseline:
    runs-on: macos-15
    steps:
      - uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10
        with:
          persist-credentials: false
      - run: make check
"""

    def test_accepts_read_only_pinned_workflow(self):
        self.assertEqual(check_baseline.workflow_policy_errors(self.workflow), [])

    def test_rejects_unpinned_action(self):
        mutated = self.workflow.replace(
            "actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10",
            "actions/checkout@v4",
        )
        self.assertNotEqual(check_baseline.workflow_policy_errors(mutated), [])

    def test_rejects_job_permission_override(self):
        mutated = self.workflow.replace(
            "    runs-on: macos-15", "    permissions:\n      contents: write\n    runs-on: macos-15"
        )
        self.assertNotEqual(check_baseline.workflow_policy_errors(mutated), [])

    def test_rejects_secret_reference(self):
        mutated = self.workflow + "      - run: echo ${{ secrets.TOKEN }}\n"
        self.assertNotEqual(check_baseline.workflow_policy_errors(mutated), [])

    def test_rejects_persisted_checkout_credentials(self):
        mutated = self.workflow.replace("persist-credentials: false", "persist-credentials: true")
        self.assertNotEqual(check_baseline.workflow_policy_errors(mutated), [])


class ToolResolutionTests(unittest.TestCase):
    @mock.patch.object(check_baseline.Path, "is_file", return_value=True)
    @mock.patch.object(check_baseline.subprocess, "run")
    def test_xcodebuild_resolution_uses_absolute_xcrun(self, run, _is_file):
        run.return_value = mock.Mock(
            returncode=0,
            stdout="/Applications/Xcode.app/Contents/Developer/usr/bin/xcodebuild\n",
            stderr="",
        )

        resolved = check_baseline.resolve_xcodebuild()

        self.assertEqual(
            resolved,
            Path("/Applications/Xcode.app/Contents/Developer/usr/bin/xcodebuild"),
        )
        run.assert_called_once_with(
            ["/usr/bin/xcrun", "--find", "xcodebuild"],
            stdout=check_baseline.subprocess.PIPE,
            stderr=check_baseline.subprocess.PIPE,
            text=True,
            check=False,
        )


class ModuleRegistrationScannerTests(unittest.TestCase):
    def setUp(self):
        self.app_delegate = (ROOT / "iOS" / "AppDelegate.m").read_text(encoding="utf-8")
        self.native_tests = (ROOT / "WowNativeReactTests" / "WowNativeReactTests.m").read_text(encoding="utf-8")

    def test_accepts_checked_in_lexical_scanner(self):
        self.assertEqual(
            check_baseline.module_registration_scanner_errors(self.app_delegate, self.native_tests),
            [],
        )

    def test_rejects_restored_raw_substring_search(self):
        mutated = self.app_delegate.replace(
            "  // Scan JavaScript tokens so registration text inside comments and strings cannot pass.\n",
            "  NSString *singleQuotedRegistration = @\"AppRegistry.registerComponent('WowNativeReact',\";\n"
            "  if ([bundleContents rangeOfString:singleQuotedRegistration].location != NSNotFound) { return YES; }\n",
            1,
        )
        self.assertNotEqual(
            check_baseline.module_registration_scanner_errors(mutated, self.native_tests),
            [],
        )

    def test_rejects_member_object_false_positive(self):
        mutated = self.app_delegate.replace("    if (previousTokenWasDot) {", "    if (NO) {", 1)
        self.assertNotEqual(
            check_baseline.module_registration_scanner_errors(mutated, self.native_tests),
            [],
        )

    def test_rejects_missing_regular_expression_handling(self):
        mutated = self.app_delegate.replace(
            "[self skipJavaScriptRegularExpressionInContents:bundleContents index:&index]",
            "NO",
            1,
        )
        self.assertNotEqual(mutated, self.app_delegate)
        self.assertNotEqual(
            check_baseline.module_registration_scanner_errors(mutated, self.native_tests),
            [],
        )

    def test_rejects_unconditional_slash_literal_handling(self):
        mutated = self.app_delegate.replace(
            "currentCharacter == '/' && canStartRegularExpression",
            "currentCharacter == '/'",
            1,
        )
        self.assertNotEqual(mutated, self.app_delegate)
        self.assertNotEqual(
            check_baseline.module_registration_scanner_errors(mutated, self.native_tests),
            [],
        )

    def test_rejects_missing_control_parenthesis_context(self):
        mutated = self.app_delegate.replace(
            "BOOL nextParenthesisStartsControlHeader = NO;",
            "BOOL nextParenthesisStartsControlHeader = YES;",
            1,
        )
        self.assertNotEqual(mutated, self.app_delegate)
        self.assertNotEqual(
            check_baseline.module_registration_scanner_errors(mutated, self.native_tests),
            [],
        )

    def test_rejects_missing_postfix_operator_context(self):
        mutated = self.app_delegate.replace(
            "(currentCharacter == '+' || currentCharacter == '-')",
            "currentCharacter == '+'",
            1,
        )
        self.assertNotEqual(mutated, self.app_delegate)
        self.assertNotEqual(
            check_baseline.module_registration_scanner_errors(mutated, self.native_tests),
            [],
        )

    def test_rejects_missing_restricted_statement_context(self):
        mutated = self.app_delegate.replace(
            "BOOL restrictedStatementCanEndAtLineTerminator = NO;",
            "BOOL restrictedStatementCanEndAtLineTerminator = YES;",
            1,
        )
        self.assertNotEqual(mutated, self.app_delegate)
        self.assertNotEqual(
            check_baseline.module_registration_scanner_errors(mutated, self.native_tests),
            [],
        )

    def test_rejects_missing_restricted_statement_native_regression(self):
        mutated = self.native_tests.replace(
            "testRejectsRegularExpressionAfterRestrictedStatement",
            "testAllowsRegularExpressionAfterRestrictedStatement",
            1,
        )
        self.assertNotEqual(mutated, self.native_tests)
        self.assertNotEqual(
            check_baseline.module_registration_scanner_errors(self.app_delegate, mutated),
            [],
        )

    def test_rejects_missing_comment_line_terminator_detection(self):
        mutated = self.app_delegate.replace(
            "[self javaScriptContents:bundleContents",
            "[self ignoredJavaScriptContents:bundleContents",
            1,
        )
        self.assertNotEqual(mutated, self.app_delegate)
        self.assertNotEqual(
            check_baseline.module_registration_scanner_errors(mutated, self.native_tests),
            [],
        )

    def test_rejects_missing_unicode_line_terminators(self):
        mutated = self.app_delegate.replace(
            "character == 0x2028 || character == 0x2029",
            "character == 0x2028",
            1,
        )
        self.assertNotEqual(mutated, self.app_delegate)
        self.assertNotEqual(
            check_baseline.module_registration_scanner_errors(mutated, self.native_tests),
            [],
        )

    def test_rejects_consumed_ambiguous_division(self):
        mutated = self.app_delegate.replace(
            "*index = regularExpressionStart;",
            "*index = length;",
            1,
        )
        self.assertNotEqual(mutated, self.app_delegate)
        self.assertNotEqual(
            check_baseline.module_registration_scanner_errors(mutated, self.native_tests),
            [],
        )


if __name__ == "__main__":
    unittest.main()
