"""Each remaining Python test file runs in exactly one Rest group.

The Rest CI job used to run every Python test outside contrib, microsimulation
and the SPM files in one pytest process. That process peaked at 15.7 GB RSS on
the 16 GB runner (CI run 37198184683), and later runs lost the runner partway
through the step. `make test-other-python-rest` now runs the same files as one
pytest process per group in REST_PYTHON_GROUPS.

Paths and --ignore flags can drop a file, or run it twice, while every test
still passes. So this guard takes each command from `make -n`, asks pytest
which files it collects, and checks that the groups together collect each file
of the old single command exactly once. The remaining group takes every file
no earlier group holds, so a new test file lands there; the check fails if a
change to the groups leaves one out.

pytest lists the files here through its own discovery (paths, --ignore,
python_files), but nothing is imported: running this file as a script swaps
each test module for a placeholder. It also skips conftest.py files, because
importing policyengine_us/conftest.py imports the whole model.
test_conftest_files_cannot_change_which_files_are_collected keeps that safe.
"""

import ast
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from collections import defaultdict
from fnmatch import fnmatch
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[3]
TESTS = REPO / "policyengine_us" / "tests"
WORKFLOWS = [REPO / ".github" / "workflows" / name for name in ("pr.yaml", "push.yaml")]
# CI runs this file under `make test-other-python-rest REST_REPORT_DIR=.`, and
# that make exports these. Passed on, they would carry its flags and report
# directory into the dry runs below.
PARENT_MAKE_VARIABLES = ("MAKEFLAGS", "MFLAGS", "MAKELEVEL", "REST_REPORT_DIR")


def dry_run(target, *overrides):
    """The commands `make <target>` runs, each split into its arguments."""
    if shutil.which("make") is None:
        pytest.skip("make is not installed")
    env = {k: v for k, v in os.environ.items() if k not in PARENT_MAKE_VARIABLES}
    result = subprocess.run(
        ["make", "-n", "--no-print-directory", target, *overrides],
        cwd=REPO,
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return [
        shlex.split(line)
        for line in result.stdout.splitlines()
        if line.startswith(("pytest ", "/usr/bin/time "))
    ]


def collected_files(args, cwd=REPO):
    """The test files pytest collects for these arguments, relative to cwd.

    A command that collects nothing (pytest's exit 5) lists no files, which
    partition_problems reports by group.
    """
    env = {k: v for k, v in os.environ.items() if k != "PYTEST_ADDOPTS"}
    with tempfile.TemporaryDirectory() as tmp:
        listing = Path(tmp) / "files.json"
        result = subprocess.run(
            [sys.executable, __file__, str(listing), *args],
            cwd=cwd,
            env=env,
            capture_output=True,
            text=True,
        )
        assert result.returncode in (0, 5), (args, result.stdout + result.stderr)
        return json.loads(listing.read_text())


def partition_problems(reference, groups):
    """How the groups' files fail to cover each reference file exactly once."""
    owners = defaultdict(list)
    for group, files in groups.items():
        for file in files:
            owners[file].append(group)
    problems = [
        f"{group} collects no files" for group, files in groups.items() if not files
    ]
    problems += [
        f"{file} is collected by no group"
        for file in sorted(set(reference) - set(owners))
    ]
    for file, file_groups in sorted(owners.items()):
        if len(file_groups) > 1:
            problems.append(f"{file} is collected by {', '.join(file_groups)}")
        if file not in reference:
            problems.append(
                f"{file} is collected by {', '.join(file_groups)} but was not "
                "in the old single process"
            )
    return problems


def rest_steps(workflow):
    return yaml.safe_load(workflow.read_text())["jobs"]["Rest"]["steps"]


def ci_report_dir(workflow):
    """The REST_REPORT_DIR a workflow's Rest job passes to the groups."""
    runs = [
        step["run"]
        for step in rest_steps(workflow)
        if "make test-other-python-rest" in step.get("run", "")
    ]
    assert len(runs) == 1, f"{workflow.name}: {len(runs)} steps run the groups"
    match = re.search(r"REST_REPORT_DIR=(\S+)", runs[0])
    assert match, f"{workflow.name} runs the groups without REST_REPORT_DIR"
    return match.group(1)


def ci_uploaded_patterns(workflow):
    """The artifact paths a workflow's Rest job uploads."""
    uploads = [
        step
        for step in rest_steps(workflow)
        if step.get("uses", "").startswith("actions/upload-artifact")
    ]
    assert len(uploads) == 1, f"{workflow.name}: {len(uploads)} upload steps"
    return uploads[0]["with"]["path"].split()


def reported_groups(report_dir):
    """Each group's pytest arguments and report files, in run order.

    The group name comes from the JUnit file, rest-python-<group>.xml.
    """
    groups = {}
    for argv in dry_run("test-other-python-rest", f"REST_REPORT_DIR={report_dir}"):
        assert argv[:3] == ["/usr/bin/time", "-v", "-o"], argv
        assert argv[4] == "pytest", argv
        junit = [arg for arg in argv[5:] if arg.startswith("--junitxml=")]
        assert len(junit) == 1, argv
        xml = junit[0].removeprefix("--junitxml=")
        match = re.fullmatch(rf"{re.escape(report_dir)}/rest-python-(.+)\.xml", xml)
        assert match, xml
        group = match.group(1)
        assert group not in groups, f"{group} runs twice"
        groups[group] = {
            "args": [arg for arg in argv[5:] if arg != junit[0]],
            "reports": [xml, argv[3]],
        }
    return groups


@pytest.fixture(scope="module")
def report_dir():
    dirs = {ci_report_dir(workflow) for workflow in WORKFLOWS}
    assert len(dirs) == 1, f"The workflows disagree on REST_REPORT_DIR: {dirs}"
    return dirs.pop()


@pytest.fixture(scope="module")
def groups(report_dir):
    return reported_groups(report_dir)


@pytest.fixture(scope="module")
def old_command():
    """The pytest arguments of the single process the groups replace.

    It was test-other-python, the Python tests outside contrib and
    microsimulation, with the SPM files left to their own step.
    """
    (other,) = dry_run("test-other-python")
    (spm,) = dry_run("test-other-python-spm")
    assert other[0] == spm[0] == "pytest", (other, spm)
    spm_files = [arg for arg in spm[1:] if not arg.startswith("-")]
    return other[1:] + [f"--ignore={file}" for file in spm_files]


def test_groups_collect_each_file_of_the_old_single_process_once(groups, old_command):
    reference = collected_files(old_command)
    # The reference is a real collection: it holds this file.
    assert Path(__file__).relative_to(REPO).as_posix() in reference
    collected = {group: collected_files(spec["args"]) for group, spec in groups.items()}
    problems = partition_problems(reference, collected)
    assert not problems, "\n".join(problems)


def test_each_group_writes_reports_the_rest_job_uploads(groups, report_dir):
    reports = [report for spec in groups.values() for report in spec["reports"]]
    assert len(set(reports)) == len(reports), reports
    for workflow in WORKFLOWS:
        patterns = [os.path.normpath(p) for p in ci_uploaded_patterns(workflow)]
        missing = [
            report
            for report in reports
            if not any(fnmatch(os.path.normpath(report), p) for p in patterns)
        ]
        assert not missing, f"{workflow.name} does not upload {missing}"


def test_groups_run_as_plain_pytest_without_a_report_dir(groups):
    """Locally the same groups run without GNU time, which macOS lacks."""
    plain = dry_run("test-other-python-rest")
    assert [argv[0] for argv in plain] == ["pytest"] * len(groups)
    assert [argv[1:] for argv in plain] == [spec["args"] for spec in groups.values()]


def test_conftest_files_cannot_change_which_files_are_collected(old_command):
    """The listing skips conftest.py; that is exact only while no conftest.py
    the Rest groups load defines collection hooks, collect_ignore or plugins."""
    ignored = [
        REPO / arg.removeprefix("--ignore=")
        for arg in old_command
        if arg.startswith("--ignore=")
    ]
    conftests = [REPO / "conftest.py", REPO / "policyengine_us" / "conftest.py"]
    conftests += sorted(TESTS.rglob("conftest.py"))
    found = []
    for conftest in conftests:
        if not conftest.exists() or any(conftest.is_relative_to(p) for p in ignored):
            continue
        for node in ast.parse(conftest.read_text()).body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                names = [node.name]
            elif isinstance(node, ast.Assign):
                names = [t.id for t in node.targets if isinstance(t, ast.Name)]
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                names = [node.target.id]
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                names = [alias.asname or alias.name for alias in node.names]
            else:
                names = []
            found += [
                f"{conftest.relative_to(REPO)}: {name}"
                for name in names
                if name.startswith(("pytest_", "collect_ignore"))
            ]
    assert not found, (
        "These can change which files pytest collects, which the listing in "
        f"this guard does not see; make it load conftest files: {found}"
    )


def write_test_files(root, names):
    for name in names:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("def test_nothing():\n    pass\n")


def test_the_check_reports_a_file_outside_every_group(tmp_path):
    write_test_files(tmp_path, ["a/test_one.py", "b/test_two.py", "new/test_new.py"])
    reference = collected_files(["."], cwd=tmp_path)
    collected = {
        "a": collected_files(["a"], cwd=tmp_path),
        "b": collected_files(["b"], cwd=tmp_path),
    }
    assert partition_problems(reference, collected) == [
        "new/test_new.py is collected by no group"
    ]


def test_the_check_reports_a_file_in_two_groups(tmp_path):
    write_test_files(tmp_path, ["a/test_one.py", "b/test_two.py"])
    reference = collected_files([".", "--ignore=b"], cwd=tmp_path)
    collected = {
        "a": collected_files(["a"], cwd=tmp_path),
        "everything": collected_files(["."], cwd=tmp_path),
    }
    assert partition_problems(reference, collected) == [
        "a/test_one.py is collected by a, everything",
        "b/test_two.py is collected by everything but was not in the old "
        "single process",
    ]


# --- Run as a script: list the files pytest collects, importing none ---------


class _Unimported(pytest.File):
    """A test file pytest would import, standing in as one placeholder item."""

    def collect(self):
        yield _Placeholder.from_parent(self, name=self.path.name)


class _Placeholder(pytest.Item):
    def runtest(self):
        raise AssertionError("listed for collection only")


class _FileListing:
    def __init__(self):
        self.files = []

    @pytest.hookimpl(tryfirst=True)
    def pytest_pycollect_makemodule(self, module_path, parent):
        return _Unimported.from_parent(parent, path=module_path)

    def pytest_collection_finish(self, session):
        # Read the kept items, not the modules built: for a file argument
        # pytest builds a module for each file beside it, then keeps one.
        self.files = [
            Path(os.path.relpath(item.path)).as_posix() for item in session.items
        ]


if __name__ == "__main__":
    output, *pytest_args = sys.argv[1:]
    listing = _FileListing()
    status = pytest.main(
        [
            *pytest_args,
            "--collect-only",
            "-q",
            "--noconftest",
            "-p",
            "no:cacheprovider",
        ],
        plugins=[listing],
    )
    Path(output).write_text(json.dumps(listing.files))
    sys.exit(status)
