"""The Push versioning job skips only when main strictly contains its commit.

The skip step's shell script is run against a stub `gh` for every status
GitHub's compare API can return, plus a failed lookup. Versioning must run
unless the status is exactly "ahead", so a stale or failed read can never
suppress the newest merge's version bump.
"""

import os
import stat
import subprocess
from pathlib import Path

import pytest
import yaml

WORKFLOW = Path(__file__).resolve().parents[3] / ".github" / "workflows" / "push.yaml"
SHA = "a" * 40


def _versioning():
    return yaml.safe_load(WORKFLOW.read_text())["jobs"]["versioning"]


def _skip_step():
    steps = [s for s in _versioning()["steps"] if s.get("id") == "head"]
    assert len(steps) == 1
    return steps[0]


def _run(tmp_path, gh_body):
    gh = tmp_path / "bin" / "gh"
    gh.parent.mkdir()
    gh.write_text("#!/bin/sh\n" + gh_body + "\n")
    gh.chmod(gh.stat().st_mode | stat.S_IEXEC)
    output = tmp_path / "output"
    output.write_text("")
    env = {
        **os.environ,
        "PATH": f"{gh.parent}{os.pathsep}{os.environ['PATH']}",
        "GITHUB_REPOSITORY": "PolicyEngine/policyengine-us",
        "GITHUB_SHA": SHA,
        "GITHUB_OUTPUT": str(output),
    }
    result = subprocess.run(
        ["bash", "-e", "-c", _skip_step()["run"]],
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    lines = [l for l in output.read_text().splitlines() if l.startswith("current=")]
    assert len(lines) == 1, lines
    return lines[0].split("=", 1)[1], result.stdout


@pytest.mark.parametrize(
    "status, current",
    [
        ("ahead", "false"),
        ("identical", "true"),
        ("behind", "true"),
        ("diverged", "true"),
        ("", "true"),
        ("null", "true"),
    ],
)
def test_skips_only_when_main_is_strictly_ahead(tmp_path, status, current):
    got, _ = _run(tmp_path, f'echo "{status}"')
    assert got == current


def test_failed_lookup_runs_versioning(tmp_path):
    got, stdout = _run(tmp_path, "echo boom >&2; exit 1")
    assert got == "true"
    assert "::warning::" in stdout


def test_compare_is_from_this_commit_to_main(tmp_path):
    got, _ = _run(
        tmp_path,
        'case "$*" in *"compare/'
        + SHA
        + '...main"*) echo ahead ;; *) echo identical ;; esac',
    )
    assert got == "false"


def test_every_later_step_is_gated_on_the_skip():
    steps = _versioning()["steps"]
    index = next(i for i, s in enumerate(steps) if s.get("id") == "head")
    for step in steps[index + 1 :]:
        assert step.get("if") == "steps.head.outputs.current == 'true'", step.get(
            "name"
        )
