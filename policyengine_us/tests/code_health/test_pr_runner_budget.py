"""Consolidating short checks must preserve coverage and failure isolation."""

import math
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
JOBS = yaml.safe_load((ROOT / ".github/workflows/pr.yaml").read_text())["jobs"]
PYTHON_WORKFLOW = yaml.safe_load(
    (ROOT / ".github/workflows/python-tests.yaml").read_text()
)
PYTHON_JOBS = PYTHON_WORKFLOW["jobs"]
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
    runner_jobs = {name: job for name, job in JOBS.items() if "uses" not in job}
    for name, job in PYTHON_JOBS.items():
        assert name not in runner_jobs
        runner_jobs[name] = job
    for name, job in runner_jobs.items():
        matrix = job.get("strategy", {}).get("matrix", {})
        if "include" in matrix:
            counts[name] = len(matrix["include"])
        else:
            counts[name] = math.prod(len(values) for values in matrix.values())
    assert sum(counts.values()) == 26
    assert {
        name: counts[name]
        for name in ("Baseline", "Contrib", "Rest", "Microsimulation")
    } == {
        "Baseline": 11,
        "Contrib": 9,
        "Rest": 1,
        "Microsimulation": 1,
    }


def test_python_group_has_two_independent_runners_and_no_extra_trigger():
    callers = [job for job in JOBS.values() if "uses" in job]
    assert callers == [
        {
            "name": "Python tests",
            "needs": "ReleaseLock",
            "uses": "./.github/workflows/python-tests.yaml",
        }
    ]
    # PyYAML parses the bare `on` key as True. No push/PR trigger here:
    # the draft guard must control the only route to these runners.
    assert PYTHON_WORKFLOW[True] == {"workflow_call": None}
    assert set(PYTHON_JOBS) == {"Rest", "Microsimulation"}
    assert {name: job["timeout-minutes"] for name, job in PYTHON_JOBS.items()} == {
        "Rest": 90,
        "Microsimulation": 60,
    }
    for job in PYTHON_JOBS.values():
        assert job["runs-on"] == "ubuntu-latest"
        assert not job.get("needs")
        assert not job.get("strategy")
        assert not job.get("continue-on-error")


def test_sequential_variants_preserve_failures_and_allow_later_results():
    for job, name, key, expected in (
        (
            "PackageCompatibility",
            "python-compat",
            "python-version",
            ["3.11", "3.12", "3.13", "3.14"],
        ),
        ("PackageCompatibility", "candidate-wheel", "kind", ["rc1", "final"]),
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
    # A wheel failure must not suppress metadata or any Python version.
    checks = [
        step
        for step in JOBS["PackageCompatibility"]["steps"]
        if step.get("uses", "").startswith("./.github/actions/")
    ]
    assert len(checks) == 7
    assert all(step["if"] == KEEP_RUNNING for step in checks[1:])


def test_variants_use_distinct_clean_checkouts_for_locks_environments_and_outputs():
    for job, name, key in (
        ("PackageCompatibility", "python-compat", "python-version"),
        ("PackageCompatibility", "candidate-wheel", "kind"),
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


def test_bundle_contract_keeps_its_dependency_and_separate_environment():
    (call,) = calls("PackageCompatibility", "bundle-metadata")
    assert call["if"] == KEEP_RUNNING
    steps = action("bundle-metadata")
    assert steps[0]["with"] == {"path": "bundle-metadata"}
    assert steps[1]["with"]["python-version"] == "3.14"
    runs = [step for step in steps if "run" in step]
    assert all(step["working-directory"] == "bundle-metadata" for step in runs)
    assert [step["run"] for step in runs] == [
        "uv lock --upgrade-package policyengine-core",
        "uv sync --locked --extra dev",
        'uv pip install --python .venv/bin/python "policyengine-bundles @ '
        "git+https://github.com/PolicyEngine/policyengine-bundles@"
        '8ae9f56fefcf89f69b8a7e3bc49928509c6207be"',
        "uv run --no-sync python -m pytest policyengine_us/tests/test_build_metadata.py",
    ]
    assert all(not step.get("continue-on-error") for step in steps)


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
