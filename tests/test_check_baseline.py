import importlib.util
import os
from pathlib import Path
import shutil
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
    def run_make(self, *arguments, environment=None):
        with tempfile.TemporaryDirectory(prefix="native react make path ") as directory:
            root = Path(directory)
            checkout = root / "checkout [hostile] 'quote"
            checkout.mkdir()
            makefile = checkout / "Makefile"
            shutil.copyfile(ROOT / "Makefile", makefile)
            external = root / "external caller"
            external.mkdir()
            env = os.environ.copy()
            if environment:
                env.update(environment)
            result = subprocess.run(
                ["make", "--no-print-directory", "-n", "-f", str(makefile), *arguments],
                cwd=external,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            return result, str(checkout)

    def test_all_aliases_preserve_spaced_absolute_makefile_path(self):
        for target in ("check", "lint", "static-check", "test", "build", "verify"):
            for name, arguments, environment in (
                ("none", (target,), None),
                ("command", (target, "ROOT=/tmp/attacker-root"), None),
                ("environment", (target,), {"ROOT": "/tmp/attacker-root"}),
            ):
                with self.subTest(target=target, override=name):
                    result, checkout = self.run_make(*arguments, environment=environment)
                    self.assertEqual(0, result.returncode, result.stderr)
                    self.assertIn(checkout, result.stdout)
                    self.assertNotIn("/tmp/attacker-root", result.stdout)

    def test_command_line_makefile_list_override_fails_closed(self):
        result, _ = self.run_make("check", "MAKEFILE_LIST=/tmp/attacker/Makefile")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("MAKEFILE_LIST must not be overridden", result.stderr)

    def test_environment_makefile_list_override_fails_closed(self):
        result, _ = self.run_make(
            "-e", "check", environment={"MAKEFILE_LIST": "/tmp/attacker/Makefile"}
        )
        self.assertNotEqual(0, result.returncode)
        self.assertIn("MAKEFILE_LIST must not be overridden", result.stderr)


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


if __name__ == "__main__":
    unittest.main()
