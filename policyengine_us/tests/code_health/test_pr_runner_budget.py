"""Consolidating short checks must preserve coverage and failure isolation."""

import math
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
JOBS = yaml.safe_load((ROOT / ".github/workflows/pr.yaml").read_text())["jobs"]
KEEP_RUNNING = "${{ !cancelled() }}"


def action(name):
    return yaml.safe_load((ROOT / f".github/actions/{name}/action.yaml").read_text())[
        "runs"
    ]["steps"]


def calls(job, name):
    return [
        step
        for step in JOBS[job]["steps"]
        if step.get("uses") == f"./.github/actions/{name}"
    ]


def test_pr_runner_budget_keeps_the_heavy_suites_separate():
    counts = {}
    for name, job in JOBS.items():
        matrix = job.get("strategy", {}).get("matrix", {})
        if "include" in matrix:
            counts[name] = len(matrix["include"])
        else:
            counts[name] = math.prod(len(values) for values in matrix.values())
    assert sum(counts.values()) == 28
    assert {
        name: counts[name]
        for name in ("Baseline", "Contrib", "Rest", "Microsimulation")
    } == {
        "Baseline": 11,
        "Contrib": 9,
        "Rest": 1,
        "Microsimulation": 1,
    }


def test_sequential_variants_preserve_failures_and_allow_later_results():
    for job, name, key, expected in (
        (
            "Python-Compat",
            "python-compat",
            "python-version",
            ["3.11", "3.12", "3.13", "3.14"],
        ),
        ("CandidateWheel", "candidate-wheel", "kind", ["rc1", "final"]),
    ):
        variants = calls(job, name)
        assert [step["with"][key] for step in variants] == expected
        assert all(step["if"] == KEEP_RUNNING for step in variants[1:])
        # A failure must remain a job failure even if a later variant passes.
        assert not JOBS[job].get("continue-on-error")
        assert all(
            not step.get("continue-on-error")
            for step in JOBS[job]["steps"] + action(name)
        )


def test_variants_use_distinct_clean_checkouts_for_locks_environments_and_outputs():
    for job, name, key in (
        ("Python-Compat", "python-compat", "python-version"),
        ("CandidateWheel", "candidate-wheel", "kind"),
    ):
        steps = action(name)
        checkout = steps[0]
        assert checkout["uses"].startswith("actions/checkout@")
        assert checkout.get("with", {}).get("clean", True)
        template = checkout["with"]["path"]
        directories = [
            template.replace("${{ inputs." + key + " }}", step["with"][key])
            for step in calls(job, name)
        ]
        assert len(set(directories)) == len(directories)
        assert all(path not in ("", ".") for path in directories)
        # uv's default .venv and modified lock/build outputs stay in each checkout.
        assert all(
            step.get("working-directory") == template for step in steps if "run" in step
        )
        if name == "candidate-wheel":
            assert (
                checkout["with"]["ref"] == "${{ github.event.pull_request.head.sha }}"
            )
            upload = next(
                step
                for step in steps
                if step.get("uses", "").startswith("actions/upload-artifact@")
            )
            assert "${{ inputs.kind }}" in upload["with"]["name"]
            assert all(
                path.startswith(template + "/")
                for path in upload["with"]["path"].splitlines()
            )


def test_every_python_version_keeps_import_and_dataset_semantics_checks():
    steps = action("python-compat")
    commands = [step["run"] for step in steps if "run" in step]
    assert "uv lock --upgrade-package policyengine-core" in commands
    assert any(
        'uv sync --locked --python "${{ inputs.python-version }}" --extra dev'
        == command
        for command in commands
    )
    assert any(
        "CountryTaxBenefitSystem, Simulation, Microsimulation" in command
        for command in commands
    )
    assert any(
        "python -m pytest policyengine_us/tests/microsimulation/data/ -q" in command
        for command in commands
    )


def test_validation_collects_independent_results_after_failure():
    steps = JOBS["ReleaseLock"]["steps"]
    runs = [step for step in steps if "run" in step]
    assert runs[0]["run"] == "python .github/release_lock.py --committed"
    for step in runs[1:]:
        assert "!cancelled()" in step["if"]
    assert all(not step.get("continue-on-error") for step in runs)
    assert any("--rehearse" in step["run"] for step in runs)
    assert any("unittest discover" in step["run"] for step in runs)
    assert any("ruff format --check" in step["run"] for step in runs)
    assert any("No valid changelog fragment found" in step["run"] for step in runs)
    assert any("git ls-files -- changelog.d" in step["run"] for step in runs)
