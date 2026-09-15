"""Release-lock regressions runnable without importing the country model.

Run: python -m unittest discover -s .github/tests -p test_release_lock.py -v
Set RELEASE_LOCK_REAL_UV=1 to exercise the installed uv against ordinary PyPI.
"""

import contextlib
import copy
import importlib.util
import io
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest
from unittest.mock import patch


HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixtures" / "registry"
SPEC = importlib.util.spec_from_file_location(
    "release_lock", HERE.parent / "release_lock.py"
)
release_lock = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(release_lock)


class RegistryFixture(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(
            prefix="country-release-lock-test-"
        )
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        for name in ("pyproject.toml", "uv.lock"):
            shutil.copyfile(FIXTURE / name, self.root / name)
        self.project = tomllib.loads((self.root / "pyproject.toml").read_text())
        self.lock = tomllib.loads((self.root / "uv.lock").read_text())
        self.original = (self.root / "uv.lock").read_bytes()

    def bump_project(self):
        path = self.root / "pyproject.toml"
        path.write_text(
            path.read_text().replace('version = "1.0.0"', 'version = "1.0.1"')
        )

    def refreshed_bytes(self):
        return self.original.replace(b'version = "1.0.0"', b'version = "1.0.1"')

    def assert_rejected(self, callback, *args, **kwargs):
        with self.assertRaises(
            (ValueError, RuntimeError, subprocess.CalledProcessError)
        ):
            callback(*args, **kwargs)


class RegistryValidationTests(RegistryFixture):
    def test_genuine_uv_registry_graph_is_accepted(self):
        release_lock.validate_registry_project(self.project)
        release_lock.validate_registry_lock(self.project, self.lock)

    def test_stale_root_version_is_rejected_before_resolver_runs(self):
        self.bump_project()
        with patch.object(release_lock.subprocess, "run") as run:
            self.assert_rejected(release_lock.check_release_lock, self.root)
        run.assert_not_called()

    def test_root_source_must_be_only_current_editable_project(self):
        for source in (
            {"editable": "../other"},
            {"virtual": "."},
            {"path": "."},
            {"editable": ".", "registry": "https://pypi.org/simple"},
        ):
            with self.subTest(source=source):
                lock = copy.deepcopy(self.lock)
                lock["package"][1]["source"] = source
                self.assert_rejected(
                    release_lock.validate_registry_lock, self.project, lock
                )

    def test_exactly_one_root_is_required_and_it_cannot_have_artifacts(self):
        missing = copy.deepcopy(self.lock)
        missing["package"].pop()
        duplicate = copy.deepcopy(self.lock)
        duplicate["package"].append(copy.deepcopy(duplicate["package"][1]))
        artifact = copy.deepcopy(self.lock)
        artifact["package"][1]["wheels"] = artifact["package"][0]["wheels"]
        for lock in (missing, duplicate, artifact):
            with self.subTest(lock=lock):
                self.assert_rejected(
                    release_lock.validate_registry_lock, self.project, lock
                )

    def test_registry_label_cannot_hide_local_or_alternate_package_sources(self):
        for source in (
            {"registry": "https://example.org/simple"},
            {"registry": "http://pypi.org/simple"},
            {"registry": "https://pypi.org/simple", "path": "/tmp/idna"},
            {"url": "https://files.pythonhosted.org/packages/idna.whl"},
            {"editable": "../idna"},
            {"path": "/tmp/idna"},
        ):
            with self.subTest(source=source):
                lock = copy.deepcopy(self.lock)
                lock["package"][0]["source"] = source
                self.assert_rejected(
                    release_lock.validate_registry_lock, self.project, lock
                )

    def test_every_sdist_and_wheel_requires_trusted_artifact_url(self):
        urls = [
            "file:///tmp/idna.whl",
            "/tmp/idna.whl",
            "../idna.whl",
            "https://example.org/packages/idna.whl",
            "http://files.pythonhosted.org/packages/idna.whl",
            "https://files.pythonhosted.org.evil.example/packages/idna.whl",
            "https://user:pass@files.pythonhosted.org/packages/idna.whl",
            "https://files.pythonhosted.org:8443/packages/idna.whl",
            "https://files.pythonhosted.org:443/packages/idna.whl",
            "https://files.pythonhosted.org/packages/idna.whl?download=1",
            "https://files.pythonhosted.org/packages/idna.whl#fragment",
            "https://files.pythonhosted.org/packages/",
            "https://files.pythonhosted.org/not-packages/idna.whl",
            "https://files.pythonhosted.org/packages/../idna.whl",
            "https://files.pythonhosted.org/packages/%2e%2e/idna.whl",
            "https://files.pythonhosted.org/packages//idna.whl",
            "https://files.pythonhosted.org/packages/a\\idna.whl",
        ]
        for kind in ("sdist", "wheel"):
            for url in urls:
                with self.subTest(kind=kind, url=url):
                    lock = copy.deepcopy(self.lock)
                    package = lock["package"][0]
                    artifact = (
                        package["sdist"] if kind == "sdist" else package["wheels"][0]
                    )
                    artifact["url"] = url
                    self.assert_rejected(
                        release_lock.validate_registry_lock, self.project, lock
                    )

    def test_every_artifact_requires_sha256_and_rejects_path_fields(self):
        mutations = [
            {"hash": None},
            {"hash": "sha256:"},
            {"hash": "sha256:" + "0" * 63},
            {"hash": "sha256:" + "g" * 64},
            {"hash": "md5:" + "a" * 32},
            {"path": "/tmp/idna.whl"},
            {"url": None},
        ]
        for kind in ("sdist", "wheel"):
            for mutation in mutations:
                with self.subTest(kind=kind, mutation=mutation):
                    lock = copy.deepcopy(self.lock)
                    package = lock["package"][0]
                    artifact = (
                        package["sdist"] if kind == "sdist" else package["wheels"][0]
                    )
                    for key, value in mutation.items():
                        if value is None:
                            artifact.pop(key, None)
                        else:
                            artifact[key] = value
                    self.assert_rejected(
                        release_lock.validate_registry_lock, self.project, lock
                    )

    def test_a_bad_later_wheel_is_also_rejected(self):
        self.lock["package"][0]["wheels"].append(
            {"url": "file:///tmp/second.whl", "hash": "sha256:" + "0" * 64}
        )
        self.assert_rejected(
            release_lock.validate_registry_lock, self.project, self.lock
        )

    def test_dependency_without_any_artifacts_is_rejected(self):
        self.lock["package"][0].pop("sdist")
        self.lock["package"][0].pop("wheels")
        self.assert_rejected(
            release_lock.validate_registry_lock, self.project, self.lock
        )

    def test_project_resolver_source_overrides_are_rejected(self):
        entries = [
            ("sources", {"idna": {"path": "../idna"}}),
            ("index", [{"url": "https://pypi.org/simple"}]),
            ("workspace", {"members": ["packages/*"]}),
            ("find-links", ["/tmp/wheels"]),
            ("index-url", "https://pypi.org/simple"),
            ("extra-index-url", ["https://example.org/simple"]),
        ]
        for key, value in entries:
            with self.subTest(key=key):
                project = copy.deepcopy(self.project)
                project["tool"] = {"uv": {key: value}}
                self.assert_rejected(release_lock.validate_registry_project, project)

    def test_direct_url_or_path_requirements_are_rejected_in_all_groups(self):
        requirements = [
            "idna @ https://files.pythonhosted.org/packages/idna.whl",
            "idna @ file:///tmp/idna",
            "idna @ ../idna",
            "../idna",
            "/tmp/idna",
        ]
        for location in ("dependencies", "optional", "group", "build"):
            for requirement in requirements:
                with self.subTest(location=location, requirement=requirement):
                    project = copy.deepcopy(self.project)
                    if location == "dependencies":
                        project["project"]["dependencies"] = [requirement]
                    elif location == "optional":
                        project["project"]["optional-dependencies"] = {
                            "dev": [requirement]
                        }
                    elif location == "group":
                        project["dependency-groups"] = {"dev": [requirement]}
                    else:
                        project["build-system"]["requires"] = [requirement]
                    self.assert_rejected(
                        release_lock.validate_registry_project, project
                    )

    def test_resolver_environment_discards_inherited_uv_and_pip_overrides(self):
        inherited = {
            "PATH": "/usr/bin",
            "UV_INDEX": "https://example.org/simple",
            "UV_FIND_LINKS": "/tmp/wheels",
            "UV_OFFLINE": "1",
            "UV_CONFIG_FILE": "/tmp/uv.toml",
            "UV_WORKING_DIRECTORY": "/tmp",
            "PIP_INDEX_URL": "https://example.org/simple",
            "PIP_FIND_LINKS": "/tmp",
        }
        with patch.dict(os.environ, inherited, clear=True):
            env = release_lock.resolver_environment()
        self.assertEqual(env["PATH"], inherited["PATH"])
        for key in inherited:
            if key.startswith(("UV_", "PIP_")):
                self.assertNotIn(key, env)


class DynamicMetadataTests(RegistryFixture):
    def test_dynamic_project_metadata_is_rejected(self):
        project = copy.deepcopy(self.project)
        project["project"]["dynamic"] = ["version"]
        self.assert_rejected(release_lock.validate_registry_project, project)


class ReleaseTransactionTests(RegistryFixture):
    def test_parent_workspace_cannot_redirect_the_lock_check(self):
        child = self.root / "members" / "child"
        child.mkdir(parents=True)
        for name in ("pyproject.toml", "uv.lock"):
            shutil.copyfile(FIXTURE / name, child / name)
        (self.root / "pyproject.toml").write_text(
            '[tool.uv.workspace]\nmembers = ["members/*"]\n'
        )
        with patch.object(release_lock.subprocess, "run") as run:
            self.assert_rejected(release_lock.check_release_lock, child)
        run.assert_not_called()
        self.assertEqual((child / "uv.lock").read_bytes(), self.original)

    def test_check_uses_uv_lock_check_without_writing_lock(self):
        with patch.object(release_lock.subprocess, "run") as run:
            release_lock.check_release_lock(self.root)
        self.assertEqual((self.root / "uv.lock").read_bytes(), self.original)
        command = run.call_args.args[0]
        self.assertIn("lock", command)
        self.assertIn("--check", command)
        self.assertIn("--no-config", command)
        self.assertIn("--no-sources", command)
        self.assertIn("https://pypi.org/simple", command)
        self.assertTrue(run.call_args.kwargs["check"])

    def test_uv_check_failure_is_not_treated_as_success(self):
        with patch.object(
            release_lock.subprocess,
            "run",
            side_effect=subprocess.CalledProcessError(1, ["uv", "lock", "--check"]),
        ):
            self.assert_rejected(release_lock.check_release_lock, self.root)
        self.assertEqual((self.root / "uv.lock").read_bytes(), self.original)

    def test_successful_check_that_changes_lock_is_rejected_and_restored(self):
        def mutate(command, **kwargs):
            (self.root / "uv.lock").write_bytes(
                self.original + b"\n# unexpected write\n"
            )
            return subprocess.CompletedProcess(command, 0)

        with patch.object(release_lock.subprocess, "run", side_effect=mutate):
            self.assert_rejected(release_lock.check_release_lock, self.root)
        self.assertEqual((self.root / "uv.lock").read_bytes(), self.original)

    def test_refresh_allows_only_root_version_change_then_checks(self):
        self.bump_project()
        commands = []

        def resolve(command, **kwargs):
            commands.append(command)
            if "--check" not in command:
                (self.root / "uv.lock").write_bytes(self.refreshed_bytes())
            return subprocess.CompletedProcess(command, 0)

        with patch.object(release_lock.subprocess, "run", side_effect=resolve):
            release_lock.check_release_lock(self.root, refresh=True)
        self.assertEqual(len(commands), 2)
        self.assertNotIn("--check", commands[0])
        self.assertIn("--check", commands[1])
        for command in commands:
            self.assertIn("--no-config", command)
            self.assertIn("--no-sources", command)
            self.assertIn("https://pypi.org/simple", command)
        current = tomllib.loads((self.root / "uv.lock").read_text())
        self.assertEqual(current["package"][1]["version"], "1.0.1")
        self.assertEqual(
            release_lock.without_root_version(current, "release-lock-fixture"),
            release_lock.without_root_version(self.lock, "release-lock-fixture"),
        )

    def test_any_reviewed_graph_drift_restores_previous_lock_bytes(self):
        mutations = {
            "dependency-version": lambda b: b.replace(
                b'version = "3.10"', b'version = "3.11"'
            ),
            "artifact-hash": lambda b: b.replace(b"12f65c9b", b"02f65c9b"),
            "root-requirement": lambda b: b.replace(b"==3.10", b">=3.10"),
            "lock-python-range": lambda b: b.replace(b">=3.11", b">=3.12"),
            "artifact-url": lambda b: b.replace(
                b"files.pythonhosted.org", b"example.org"
            ),
        }
        self.bump_project()
        for name, mutate in mutations.items():
            with self.subTest(name=name):

                def resolve(command, **kwargs):
                    (self.root / "uv.lock").write_bytes(mutate(self.refreshed_bytes()))
                    return subprocess.CompletedProcess(command, 0)

                with patch.object(release_lock.subprocess, "run", side_effect=resolve):
                    self.assert_rejected(
                        release_lock.check_release_lock, self.root, refresh=True
                    )
                self.assertEqual((self.root / "uv.lock").read_bytes(), self.original)

    def test_network_failure_after_partial_write_restores_previous_lock_bytes(self):
        self.bump_project()

        def fail(command, **kwargs):
            (self.root / "uv.lock").write_bytes(b"partial resolver output\n")
            raise subprocess.CalledProcessError(
                2, command, stderr="network unavailable"
            )

        with patch.object(release_lock.subprocess, "run", side_effect=fail):
            self.assert_rejected(
                release_lock.check_release_lock, self.root, refresh=True
            )
        self.assertEqual((self.root / "uv.lock").read_bytes(), self.original)

    def test_interrupted_refresh_restores_a_deleted_previous_lock(self):
        self.bump_project()

        def interrupt(command, **kwargs):
            (self.root / "uv.lock").unlink()
            raise KeyboardInterrupt()

        with patch.object(release_lock.subprocess, "run", side_effect=interrupt):
            with self.assertRaises(KeyboardInterrupt):
                release_lock.check_release_lock(self.root, refresh=True)
        self.assertEqual((self.root / "uv.lock").read_bytes(), self.original)

    def test_post_refresh_check_failure_restores_previous_lock_bytes(self):
        self.bump_project()

        def resolve(command, **kwargs):
            if "--check" in command:
                raise subprocess.CalledProcessError(1, command)
            (self.root / "uv.lock").write_bytes(self.refreshed_bytes())
            return subprocess.CompletedProcess(command, 0)

        with patch.object(release_lock.subprocess, "run", side_effect=resolve):
            self.assert_rejected(
                release_lock.check_release_lock, self.root, refresh=True
            )
        self.assertEqual((self.root / "uv.lock").read_bytes(), self.original)

    def test_invalid_previous_artifact_is_rejected_without_resolver(self):
        invalid = self.original.replace(
            b"https://files.pythonhosted.org", b"file:///tmp"
        )
        (self.root / "uv.lock").write_bytes(invalid)
        self.bump_project()
        with patch.object(release_lock.subprocess, "run") as run:
            self.assert_rejected(
                release_lock.check_release_lock, self.root, refresh=True
            )
        run.assert_not_called()
        self.assertEqual((self.root / "uv.lock").read_bytes(), invalid)


class RehearsalTests(RegistryFixture):
    """The rehearsal runs the release refresh on a copy, never on the checkout."""

    def copy_resolver(self, mutate=None):
        """Stand in for uv: write the refreshed lock wherever it is invoked."""
        self.calls = []

        def resolve(command, **kwargs):
            cwd = Path(kwargs["cwd"])
            self.calls.append(
                {
                    "command": command,
                    "cwd": cwd,
                    "contents": sorted(entry.name for entry in cwd.iterdir()),
                    "project": (cwd / "pyproject.toml").read_text(),
                    "lock": (cwd / "uv.lock").read_bytes(),
                }
            )
            if "--check" not in command:
                refreshed = self.refreshed_bytes()
                (cwd / "uv.lock").write_bytes(
                    refreshed if mutate is None else mutate(refreshed)
                )
            return subprocess.CompletedProcess(command, 0)

        return resolve

    def assert_checkout_untouched(self):
        self.assertEqual((self.root / "uv.lock").read_bytes(), self.original)
        self.assertIn('version = "1.0.0"', (self.root / "pyproject.toml").read_text())

    def test_rehearsal_bumps_a_copy_and_accepts_a_root_only_refresh(self):
        with patch.object(
            release_lock.subprocess, "run", side_effect=self.copy_resolver()
        ):
            version = release_lock.rehearse_release_lock(self.root)
        self.assertEqual(version, "1.0.1")
        self.assert_checkout_untouched()
        self.assertEqual(len(self.calls), 2)
        for call in self.calls:
            self.assertNotEqual(call["cwd"], self.root)
            # uv resolves the copy from project metadata alone, with no
            # package tree, and the copy is removed when the run ends.
            self.assertEqual(call["contents"], ["pyproject.toml", "uv.lock"])
            self.assertFalse(call["cwd"].exists())
            self.assertIn('version = "1.0.1"', call["project"])
            self.assertIn("--no-config", call["command"])
            self.assertIn("--no-sources", call["command"])
            self.assertIn("https://pypi.org/simple", call["command"])
        self.assertNotIn("--check", self.calls[0]["command"])
        self.assertEqual(self.calls[0]["lock"], self.original)
        self.assertIn("--check", self.calls[1]["command"])
        self.assertEqual(self.calls[1]["lock"], self.refreshed_bytes())

    def test_rehearsal_rejects_a_resolver_that_rewrites_resolution_markers(self):
        # The 2026-09-11 release failure: a lock written by one uv version, and
        # re-resolved by another, keeps every package but renormalizes markers.
        def renormalize(data):
            return data.replace(
                b'requires-python = ">=3.11"\n',
                b'requires-python = ">=3.11"\n'
                b"resolution-markers = [\n"
                b"    \"python_full_version >= '3.12'\",\n"
                b"    \"python_full_version < '3.12'\",\n"
                b"]\n",
            )

        with patch.object(
            release_lock.subprocess, "run", side_effect=self.copy_resolver(renormalize)
        ):
            with self.assertRaisesRegex(
                ValueError, "changed the reviewed dependency graph"
            ):
                release_lock.rehearse_release_lock(self.root)
        self.assert_checkout_untouched()

    def test_rehearsal_reports_a_resolver_failure_without_touching_the_checkout(self):
        with patch.object(
            release_lock.subprocess,
            "run",
            side_effect=subprocess.CalledProcessError(1, ["uv", "lock"]),
        ):
            self.assert_rejected(release_lock.rehearse_release_lock, self.root)
        self.assert_checkout_untouched()

    def test_rehearsal_rejects_a_resolver_that_writes_to_the_checkout(self):
        def stray(command, **kwargs):
            (self.root / "uv.lock").write_bytes(self.original + b"\n# stray write\n")
            (Path(kwargs["cwd"]) / "uv.lock").write_bytes(self.refreshed_bytes())
            return subprocess.CompletedProcess(command, 0)

        with patch.object(release_lock.subprocess, "run", side_effect=stray):
            with self.assertRaisesRegex(ValueError, "must not change uv.lock"):
                release_lock.rehearse_release_lock(self.root)

    def test_rehearsal_refuses_a_checkout_inside_a_uv_workspace(self):
        child = self.root / "members" / "child"
        child.mkdir(parents=True)
        for name in ("pyproject.toml", "uv.lock"):
            shutil.copyfile(FIXTURE / name, child / name)
        (self.root / "pyproject.toml").write_text(
            '[tool.uv.workspace]\nmembers = ["members/*"]\n'
        )
        with patch.object(release_lock.subprocess, "run") as run:
            self.assert_rejected(release_lock.rehearse_release_lock, child)
        run.assert_not_called()

    def test_rehearsed_bump_matches_the_release_bump(self):
        """The rehearsal applies the patch bump bump_version.py would apply."""
        spec = importlib.util.spec_from_file_location(
            "bump_version", HERE.parent / "bump_version.py"
        )
        bump_version = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(bump_version)
        probe = self.root / "probe-pyproject.toml"
        for source in (FIXTURE / "pyproject.toml", HERE.parents[1] / "pyproject.toml"):
            with self.subTest(source=source.parent.name):
                shutil.copyfile(source, probe)
                current = bump_version.get_current_version(probe)
                expected = bump_version.bump_version(current, "patch")
                with contextlib.redirect_stdout(io.StringIO()):
                    bump_version.update_file(probe, current, expected)
                project, version = release_lock.bumped_project(source.read_text())
                self.assertEqual(version, expected)
                self.assertEqual(project, probe.read_text())


class RehearsalCommandTests(unittest.TestCase):
    def test_rehearse_cannot_combine_with_the_other_modes(self):
        for flags in (["--rehearse", "--committed"], ["--rehearse", "--refresh"]):
            with self.subTest(flags=flags):
                with patch.object(sys, "argv", ["release_lock.py", *flags]):
                    with contextlib.redirect_stderr(io.StringIO()) as reported:
                        with self.assertRaises(SystemExit) as raised:
                            release_lock.main()
                self.assertEqual(raised.exception.code, 2)
                self.assertIn("not allowed with argument", reported.getvalue())

    def test_rehearsal_failure_exits_two_with_the_hint(self):
        with patch.object(
            release_lock,
            "rehearse_release_lock",
            side_effect=ValueError("Versioning changed the reviewed dependency graph"),
        ):
            with patch.object(sys, "argv", ["release_lock.py", "--rehearse"]):
                with contextlib.redirect_stderr(io.StringIO()) as reported:
                    with self.assertRaises(SystemExit) as raised:
                        release_lock.main()
        self.assertEqual(raised.exception.code, 2)
        self.assertIn("regenerate uv.lock with the pinned uv", reported.getvalue())
        self.assertIn(
            "Versioning changed the reviewed dependency graph", reported.getvalue()
        )


class CommittedLockTests(RegistryFixture):
    def setUp(self):
        super().setUp()
        self.git("init", "-q")
        self.git("add", "pyproject.toml", "uv.lock")
        self.git(
            "-c",
            "user.name=Release Lock Test",
            "-c",
            "user.email=release-lock@example.invalid",
            "-c",
            "commit.gpgsign=false",
            "commit",
            "-qm",
            "Registry fixture",
        )

    def git(self, *args):
        return subprocess.run(
            ["git", *args], cwd=self.root, check=True, capture_output=True
        )

    def test_committed_check_accepts_exact_head_files(self):
        real_run = subprocess.run

        def resolve(command, **kwargs):
            if command[0] == "git":
                return real_run(command, **kwargs)
            return subprocess.CompletedProcess(command, 0)

        with patch.object(release_lock.subprocess, "run", side_effect=resolve):
            release_lock.check_release_lock(self.root, committed=True)

    def test_committed_check_rejects_uncommitted_lock_and_project(self):
        for filename in ("uv.lock", "pyproject.toml"):
            with self.subTest(filename=filename):
                path = self.root / filename
                previous = path.read_bytes()
                path.write_bytes(previous + b"\n# Uncommitted local regeneration\n")
                try:
                    self.assert_rejected(
                        release_lock.check_release_lock, self.root, committed=True
                    )
                finally:
                    path.write_bytes(previous)


@unittest.skipUnless(
    os.environ.get("RELEASE_LOCK_REAL_UV") == "1",
    "set RELEASE_LOCK_REAL_UV=1 for the real registry resolver probe",
)
class RealUvTests(RegistryFixture):
    def lock_with_installed_uv(self):
        """Write the fixture lock as the installed uv version normalizes it."""
        command = [
            "uv",
            "lock",
            "--no-config",
            "--no-sources",
            "--default-index",
            "https://pypi.org/simple",
            "--cache-dir",
            str(self.root / "cache"),
        ]
        subprocess.run(
            command,
            cwd=self.root,
            env=release_lock.resolver_environment(),
            check=True,
            timeout=60,
        )

    def test_actual_registry_root_only_refresh(self):
        """Resolve genuine PyPI idna, bump only root, and check the final graph."""
        self.lock_with_installed_uv()
        before = tomllib.loads((self.root / "uv.lock").read_text())
        release_lock.check_release_lock(self.root)
        self.bump_project()
        release_lock.check_release_lock(self.root, refresh=True)
        after = tomllib.loads((self.root / "uv.lock").read_text())
        self.assertEqual(after["package"][1]["version"], "1.0.1")
        self.assertEqual(
            release_lock.without_root_version(before, "release-lock-fixture"),
            release_lock.without_root_version(after, "release-lock-fixture"),
        )
        release_lock.check_release_lock(self.root)

    def test_actual_registry_rehearsal_leaves_the_checkout_alone(self):
        """Rehearse the release bump against real PyPI, on a copy of the root."""
        self.lock_with_installed_uv()
        before = (self.root / "uv.lock").read_bytes()
        project = (self.root / "pyproject.toml").read_bytes()
        version = release_lock.rehearse_release_lock(self.root)
        self.assertEqual(version, "1.0.1")
        self.assertEqual((self.root / "uv.lock").read_bytes(), before)
        self.assertEqual((self.root / "pyproject.toml").read_bytes(), project)


if __name__ == "__main__":
    unittest.main()
