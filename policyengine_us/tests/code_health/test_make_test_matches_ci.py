"""`make test` runs what CI runs, and only in bounded subprocesses.

CI splits the suites into batched subprocesses so none outgrows a 16 GB
runner. `make test` used to run the whole policy tree in one
`policyengine-core test` process instead, and a 1,500-file baseline run of
that shape reached 118 GB on a 128 GB Mac (2026-10-02). These checks keep the
local full run equal to CI's suites and free of single-process tree runs.
"""

import re
import shlex
import shutil
import subprocess
from functools import lru_cache
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "pr.yaml"
SHARD = re.compile(r"\s+--shard\s+\d+/\d+")
MAKE_TARGET = re.compile(r"\bmake\s+([\w-]+)")
# CI's planned Rest Python shards run this target's groups; the planner reads
# them from its dry run (code_health/test_rest_python_groups.py).
PLANNED_TARGETS = {"rest_python_shards.py run": "test-other-python-rest"}

pytestmark = pytest.mark.skipif(
    shutil.which("make") is None or not WORKFLOW.exists(),
    reason="needs make and the repository's CI workflow",
)


@lru_cache(maxsize=None)
def make_commands(target: str) -> frozenset:
    """The shell commands ``make <target>`` would run, comments dropped."""
    output = subprocess.run(
        ["make", "-n", target],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return frozenset(
        line.strip()
        for line in output.splitlines()
        if line.strip() and not line.strip().startswith("#")
    )


def workflow_jobs(path):
    """Include suites in local reusable workflows as well as direct jobs."""
    for job in yaml.safe_load(path.read_text())["jobs"].values():
        if "uses" in job:
            assert job["uses"].startswith("./.github/workflows/"), job["uses"]
            yield from workflow_jobs(REPO_ROOT / job["uses"])
        else:
            yield job


def ci_suites():
    """Every Make target and batch-runner command the PR workflow runs."""
    targets, commands = set(), set()
    for job in workflow_jobs(WORKFLOW):
        matrix = (job.get("strategy") or {}).get("matrix") or {}
        # A planned matrix is an expression; its steps name the target.
        entries = [] if isinstance(matrix, str) else matrix.get("include") or []
        for entry in entries:
            if "target" in entry:
                targets.add(entry["target"])
            if "cmd" in entry:
                cmd = entry["cmd"]
                targets.update(MAKE_TARGET.findall(cmd))
                if "test_batched.py" in cmd:
                    commands.add(cmd.strip())
        for step in job.get("steps") or []:
            for target in MAKE_TARGET.findall(step.get("run") or ""):
                if not target.startswith("$"):
                    targets.add(target)
            for command, target in PLANNED_TARGETS.items():
                if command in (step.get("run") or ""):
                    targets.add(target)
    return {t for t in targets if t.startswith("test")}, commands


def test_make_test_runs_every_ci_suite():
    local = make_commands("test")
    targets, commands = ci_suites()
    assert targets, "found no Make targets in the CI workflow"
    missing = {
        target: sorted(make_commands(target) - local)
        for target in sorted(targets)
        if make_commands(target) - local
    }
    # A sharded CI command runs one shard; locally the unsharded command
    # runs every shard of the same batches.
    missing.update(
        {cmd: [] for cmd in sorted(commands) if SHARD.sub("", cmd) not in local}
    )
    assert not missing, f"make test skips CI suites: {missing}"


def test_make_test_never_runs_a_whole_tree_in_one_process():
    single_process = [
        command
        for command in make_commands("test")
        if re.search(
            r"policyengine(-core|_core\.scripts\.policyengine_command) test", command
        )
    ]
    assert not single_process, (
        "run YAML suites through policyengine_us/tests/test_batched.py, "
        f"not one policyengine-core process: {single_process}"
    )


def test_contrib_ssa_yaml_has_a_dedicated_single_file_serial_route():
    """Local/CI equality alone missed SSA when both routes excluded its YAML.

    Its large reform combinations need separate files and an effective
    one-worker limit even when CI exports POLICYENGINE_BATCH_WORKERS=2.
    """
    root = "policyengine_us/tests/policy/contrib"
    ssa = f"{root}/ssa"
    assert any((REPO_ROOT / ssa).rglob("*.yaml")), "SSA YAML coverage is absent"
    commands = make_commands("test-yaml-structural-other")
    batcher = "policyengine_us/tests/test_batched.py"
    batch_commands = [
        shlex.split(command) for command in commands if batcher in command
    ]
    dedicated = [arguments for arguments in batch_commands if ssa in arguments]
    assert len(dedicated) == 1, "SSA must have one dedicated YAML invocation"
    (arguments,) = dedicated
    assert arguments[arguments.index("--mode") + 1] == "per-file"
    assert arguments[arguments.index("--workers") + 1] == "1"
    assert "POLICYENGINE_BATCH_WORKERS=1" in arguments

    generic = [arguments for arguments in batch_commands if root in arguments]
    assert len(generic) == 1
    (arguments,) = generic
    excluded = arguments[arguments.index("--exclude") + 1].split(",")
    assert "ssa" in excluded, "SSA YAML must not also enter a shared subdir batch"
    assert commands <= make_commands("test"), "The full suite must retain SSA's route"


@pytest.mark.parametrize("workflow_name", ("python-tests.yaml", "push.yaml"))
def test_microsimulation_fetches_the_pinned_social_security_reference(workflow_name):
    """A shallow CI checkout otherwise skips every legacy differential case."""
    source = (
        REPO_ROOT
        / "policyengine_us/tests/microsimulation/test_social_security_current_law.py"
    ).read_text()
    reference = re.search(
        r"^REVIEWED_MAIN_SHA = [\"']([0-9a-f]{40})[\"']$", source, re.MULTILINE
    )
    assert reference, "the differential must declare its reviewed main commit"
    expected_fetch = [
        "git",
        "fetch",
        "--no-tags",
        "--depth=1",
        "origin",
        reference.group(1),
    ]
    workflow = yaml.safe_load(
        (REPO_ROOT / ".github/workflows" / workflow_name).read_text()
    )
    steps = workflow["jobs"]["Microsimulation"]["steps"]
    fetch_steps = [
        index
        for index, step in enumerate(steps)
        for line in (step.get("run") or "").splitlines()
        if shlex.split(line) == expected_fetch
    ]
    test_steps = [
        index
        for index, step in enumerate(steps)
        if "test-microsimulation" in MAKE_TARGET.findall(step.get("run") or "")
    ]
    assert len(fetch_steps) == 1, "fetch the exact pre-feature reference once"
    assert len(test_steps) == 1, "the microsimulation suite must run once"
    assert fetch_steps[0] < test_steps[0], "fetch the reference before the suite runs"
