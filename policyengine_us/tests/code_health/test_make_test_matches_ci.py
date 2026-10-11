"""`make test` runs what CI runs, and only in bounded subprocesses.

CI splits the suites into batched subprocesses so none outgrows a 16 GB
runner. `make test` used to run the whole policy tree in one
`policyengine-core test` process instead, and a 1,500-file baseline run of
that shape reached 118 GB on a 128 GB Mac (2026-10-02). These checks keep the
local full run equal to CI's suites and free of single-process tree runs.
"""

import re
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
        for entry in matrix.get("include") or []:
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
