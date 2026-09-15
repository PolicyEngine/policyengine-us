"""Release artifact contracts without importing the country model."""

import importlib.util
import json
from pathlib import Path
import re
import subprocess
import tempfile
import tomllib
import unittest
from unittest.mock import patch
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "release_build", ROOT / ".github/release_build.py"
)
release_build = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(release_build)


def job(text, name):
    return re.search(
        rf"^  {name}:\n(.*?)(?=^  [A-Za-z]|\Z)", text, re.MULTILINE | re.DOTALL
    )[1]


class WorkflowTests(unittest.TestCase):
    def test_candidate_build_matches_publish_without_publication_or_policy_mutations(
        self,
    ):
        pr = (ROOT / ".github/workflows/pr.yaml").read_text()
        candidate = job(pr, "CandidateWheel")
        publish = job((ROOT / ".github/workflows/push.yaml").read_text(), "Publish")
        commands = (
            "python .github/release_lock.py --committed",
            'python .github/release_build.py --prepare "${{ matrix.kind }}"',
            "python .github/release_lock.py --refresh",
            "uv sync --locked --extra dev",
            "uv run --no-sync make",
            "uv run --no-sync python .github/release_build.py",
            "actions/upload-artifact@",
        )
        self.assertEqual(
            [candidate.index(value) for value in commands],
            sorted(candidate.index(value) for value in commands),
        )
        self.assertIn("github.event.pull_request.head.sha", candidate)
        self.assertIn("kind: [rc1, final]", candidate)
        self.assertIn("release-wheel-${{ matrix.kind }}-", candidate)
        for expected in (
            "runs-on: ubuntu-24.04",
            'python-version: "3.14.7"',
            'version: "0.12.13"',
            "uv sync --locked --extra dev",
            "uv run --no-sync make",
            "python .github/release_build.py",
        ):
            self.assertIn(expected, candidate)
            self.assertIn(expected, publish)
        for prohibited in (
            "update_itemization",
            "pypi-publish",
            "secrets.",
            "git push",
            "contents: write",
        ):
            self.assertNotIn(prohibited, candidate)
        self.assertIn("dist/*.whl", candidate)
        self.assertIn("release-build/receipt.json", candidate)
        self.assertNotIn("run: uv build", job(pr, "Quick-Feedback"))
        self.assertLess(
            publish.index("python .github/release_build.py"),
            publish.index("pypa/gh-action-pypi-publish"),
        )

    def test_isolated_backend_closure_is_exactly_pinned(self):
        project = tomllib.loads((ROOT / "pyproject.toml").read_text())
        pins = release_build.checked_build_requirements(project)
        self.assertEqual(
            set(pins),
            {
                "hatchling",
                "packaging",
                "pathspec",
                "pluggy",
                "tomlkit",
                "trove-classifiers",
            },
        )
        project["build-system"]["requires"][0] = "hatchling>=1.32"
        with self.assertRaises(ValueError):
            release_build.checked_build_requirements(project)


class PreparationTests(unittest.TestCase):
    def test_each_candidate_uses_actual_fragment_version_helper(self):
        for category, next_version in (
            ("fixed", "4.2.4"),
            ("added", "4.3.0"),
            ("breaking", "5.0.0"),
        ):
            for kind in ("rc1", "final"):
                with self.subTest(category=category, kind=kind):
                    with tempfile.TemporaryDirectory() as temporary:
                        root = Path(temporary)
                        (root / ".github").mkdir()
                        (root / ".github/bump_version.py").write_bytes(
                            (ROOT / ".github/bump_version.py").read_bytes()
                        )
                        (root / "changelog.d").mkdir()
                        (root / f"changelog.d/test.{category}.md").write_text(
                            "Change\n"
                        )
                        project = root / "pyproject.toml"
                        project.write_text('[project]\nversion = "4.2.3"\n')
                        release_build.prepare_candidate(root, kind)
                        expected = next_version + ("rc1" if kind == "rc1" else "")
                        self.assertEqual(
                            tomllib.loads(project.read_text())["project"]["version"],
                            expected,
                        )


class ReceiptTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="release-artifact-test-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.policy = self.root / "policyengine_us" / "parameter.yaml"
        self.policy.parent.mkdir()
        self.policy.write_text("branching: true\n")
        (self.root / "pyproject.toml").write_text(
            '[project]\nversion = "1.0.0"\n[build-system]\nrequires = ["hatchling==1.32.0"]\nbuild-backend = "hatchling.build"\n'
        )
        (self.root / "uv.lock").write_text(
            '[[package]]\nname = "build"\nversion = "1.4.0"\n'
        )
        for args in (
            ("init", "-q"),
            ("add", "."),
            (
                "-c",
                "user.name=Fixture",
                "-c",
                "user.email=fixture@example.invalid",
                "commit",
                "-qm",
                "fixture",
            ),
        ):
            subprocess.run(
                ["git", *args], cwd=self.root, check=True, capture_output=True
            )
        (self.root / "dist").mkdir()
        self.wheel = self.root / "dist" / "policyengine_us-1.0.0-py3-none-any.whl"
        self.write_wheel()

    def write_wheel(self, version="1.0.0", generator="hatchling 1.32.0"):
        with ZipFile(self.wheel, "w") as wheel:
            wheel.writestr("policyengine_us/parameter.yaml", self.policy.read_bytes())
            wheel.writestr(
                "policyengine_us-1.0.0.dist-info/METADATA",
                f"Name: policyengine-us\nVersion: {version}\n",
            )
            wheel.writestr(
                "policyengine_us-1.0.0.dist-info/WHEEL",
                f"Wheel-Version: 1.0\nGenerator: {generator}\n",
            )

    def test_receipt_binds_actual_wheel_and_permits_only_root_version_preparation(self):
        project_path = self.root / "pyproject.toml"
        project_path.write_text(project_path.read_text().replace('"1.0.0"', '"1.0.1"'))
        self.write_wheel(version="1.0.1")
        with patch.object(release_build, "version", return_value="1.4.0"):
            output = release_build.write_build_receipt(self.root)
        receipt = json.loads(output.read_text())
        self.assertEqual(receipt["prepared_version"], "1.0.1")
        self.assertEqual(receipt["wheel"]["sha256"], release_build._sha256(self.wheel))
        self.assertTrue(receipt["policy_source_matches_head"])
        self.assertEqual(receipt["frontend"]["version"], "1.4.0")

    def test_changed_policy_parameter_is_rejected_before_receipt(self):
        self.policy.write_text("branching: false\n")
        with self.assertRaises(subprocess.CalledProcessError):
            release_build.write_build_receipt(self.root)
        self.assertFalse((self.root / "release-build/receipt.json").exists())

    def test_untracked_policy_source_is_rejected(self):
        (self.policy.parent / "extra.py").write_text("pass\n")
        with self.assertRaisesRegex(ValueError, "Untracked policy source"):
            release_build.write_build_receipt(self.root)

    def test_wrong_generator_or_version_is_rejected(self):
        for version, generator in (
            ("1.0.1", "hatchling 1.32.0"),
            ("1.0.0", "hatchling 1.31.0"),
        ):
            self.write_wheel(version=version, generator=generator)
            with self.assertRaises(ValueError):
                release_build.wheel_identity(
                    self.wheel, expected_version="1.0.0", hatchling_version="1.32.0"
                )

    def test_frontend_drift_is_rejected(self):
        with patch.object(release_build, "version", return_value="1.6.1"):
            with self.assertRaisesRegex(ValueError, "frontend differs"):
                release_build.write_build_receipt(self.root)
