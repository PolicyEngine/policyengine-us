"""Consolidating short checks must preserve coverage and failure isolation."""

import math
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[3]
JOBS = yaml.safe_load((ROOT / ".github/workflows/pr.yaml").read_text())["jobs"]
GROUP_WORKFLOWS = {
    name: yaml.safe_load((ROOT / job["uses"]).read_text())
    for name, job in JOBS.items()
    if "uses" in job
}
PYTHON_JOBS = GROUP_WORKFLOWS["PythonTests"]["jobs"]
KEEP_RUNNING = "${{ !cancelled() }}"
READY_GUARD = "github.event.pull_request.draft == false"
MAIN_ONLY = "github.base_ref == 'main'"
CHEAP_JOBS = {"ReleaseLock", "PackageCompatibility", "Quick-Feedback"}
JOB_DEPENDENCIES_AND_GUARDS = {
    "ReleaseLock": {"if": READY_GUARD},
    "PackageCompatibility": {"needs": "ReleaseLock"},
    "Quick-Feedback": {"needs": "ReleaseLock"},
    "Baseline": {"needs": "ReleaseLock", "if": MAIN_ONLY},
    "HouseholdAPIPartners": {"needs": "ReleaseLock", "if": MAIN_ONLY},
    "Contrib": {"needs": "ReleaseLock", "if": MAIN_ONLY},
    "PythonTests": {"needs": "ReleaseLock", "if": MAIN_ONLY},
}
# The main PR runner layout before the integration pilot, including each shard.
MAIN_RUNNER_COUNTS = {
    "ReleaseLock": 1,
    "PackageCompatibility": 1,
    "Quick-Feedback": 1,
    "HouseholdAPIPartners": 1,
    "Baseline": 11,
    "Contrib": 9,
    "Rest": 1,
    "Microsimulation": 1,
}


def eligible_jobs(base, draft, failed_jobs=()):
    """Model supported guards and the implicit successful dependency requirement."""
    conditions = {None: True, READY_GUARD: not draft, MAIN_ONLY: base == "main"}

    def eligible(name):
        job = JOBS[name]
        condition = job.get("if")
        assert condition in conditions, (name, condition)
        needs = job.get("needs", [])
        if isinstance(needs, str):
            needs = [needs]
        return conditions[condition] and all(
            parent not in failed_jobs and eligible(parent) for parent in needs
        )

    return {name for name in JOBS if eligible(name)}


def runner_counts(job_names):
    runner_jobs = {}
    for name in job_names:
        if name in GROUP_WORKFLOWS:
            additions = GROUP_WORKFLOWS[name]["jobs"]
        else:
            additions = {name: JOBS[name]}
        assert not runner_jobs.keys() & additions.keys()
        runner_jobs.update(additions)
    counts = {}
    for name, job in runner_jobs.items():
        matrix = job.get("strategy", {}).get("matrix", {})
        if "include" in matrix:
            counts[name] = len(matrix["include"])
        else:
            counts[name] = math.prod(len(values) for values in matrix.values())
    return counts


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
    counts = runner_counts(eligible_jobs("main", draft=False))
    assert counts == MAIN_RUNNER_COUNTS
    assert sum(counts.values()) == 26


@pytest.mark.parametrize(
    "base,draft,expected",
    [
        ("main", False, MAIN_RUNNER_COUNTS),
        ("integration", False, {name: 1 for name in CHEAP_JOBS}),
        ("main", True, {}),
        ("integration", True, {}),
    ],
)
def test_pr_jobs_and_runner_budget_by_base_and_draft(base, draft, expected):
    assert {
        name: {key: job[key] for key in ("needs", "if") if key in job}
        for name, job in JOBS.items()
    } == JOB_DEPENDENCIES_AND_GUARDS
    jobs = eligible_jobs(base, draft)
    assert runner_counts(jobs) == expected
    if base == "integration" and not draft:
        assert jobs == CHEAP_JOBS


@pytest.mark.parametrize("base", ["main", "integration"])
def test_failed_release_lock_prevents_all_dependent_runners(base):
    # The exact needs/if contract above rules out bypassing dependency success
    # with always() or a status guard. This bounded model checks the intended
    # failure route, including main-only suites; static YAML cannot verify
    # GitHub's live expression evaluation or actual scheduling after a failure.
    jobs = eligible_jobs(base, draft=False, failed_jobs={"ReleaseLock"})
    assert jobs == {"ReleaseLock"}
    assert runner_counts(jobs) == {"ReleaseLock": 1}
    assert all(not job.get("continue-on-error") for job in JOBS.values())


def test_main_runner_checks_and_matrix_members_are_unchanged():
    assert set(eligible_jobs("main", draft=False)) == {
        "ReleaseLock",
        "PackageCompatibility",
        "Quick-Feedback",
        "Baseline",
        "HouseholdAPIPartners",
        "Contrib",
        "PythonTests",
    }
    assert {name: JOBS[name]["name"] for name in CHEAP_JOBS} == {
        "ReleaseLock": "PR validation (lock, guard tests, lint, changelog)",
        "PackageCompatibility": "Package and compatibility",
        "Quick-Feedback": "Quick Feedback (Selective Tests + Coverage)",
    }
    assert JOBS["HouseholdAPIPartners"]["name"] == "Household API Partners"
    for name, expected_groups in {
        "Baseline": [
            "states-shard-1",
            "states-shard-2",
            "states-shard-3",
            "states-shard-4",
            "irs",
            "household",
            "ssa-usda",
            "rest-a",
            "rest-b",
            "contrib-hhs",
            "reform",
        ],
        "Contrib": [
            "states-shard-1",
            "states-shard-2",
            "states-shard-3",
            "states-shard-4",
            "other-shard-1",
            "other-shard-2a",
            "other-shard-2b",
            "other-shard-3",
            "congress",
        ],
    }.items():
        job = GROUP_WORKFLOWS[name]["jobs"][name]
        assert job["name"] == f"Full Suite - {name} (${{{{ matrix.group }}}})"
        assert [item["group"] for item in job["strategy"]["matrix"]["include"]] == (
            expected_groups
        )
    assert {name: job["name"] for name, job in PYTHON_JOBS.items()} == {
        "Rest": "Full Suite - Rest (Python + variables)",
        "Microsimulation": "Full Suite - Microsimulation",
    }


def test_suite_groups_have_no_extra_runners_or_triggers():
    groups = {
        "Baseline": ("Baseline tests", "baseline-tests.yaml"),
        "Contrib": ("Contrib tests", "contrib-tests.yaml"),
        "PythonTests": ("Python tests", "python-tests.yaml"),
    }
    assert set(GROUP_WORKFLOWS) == set(groups)
    for name, (label, file) in groups.items():
        assert JOBS[name] == {
            "name": label,
            "needs": "ReleaseLock",
            "if": MAIN_ONLY,
            "uses": f"./.github/workflows/{file}",
        }
        # PyYAML parses the bare `on` key as True. No push/PR trigger here:
        # the draft guard must control the only route to these runners.
        assert GROUP_WORKFLOWS[name][True] == {"workflow_call": None}
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


def test_cheap_checks_use_the_actual_pr_base_or_checked_out_commit():
    validation = JOBS["ReleaseLock"]["steps"]
    checkout = validation[0]
    assert checkout["uses"].startswith("actions/checkout@")
    assert checkout["with"] == {"fetch-depth": 2}
    # The changelog check uses the checked-out merge and its first parent.
    changelog = next(
        step
        for step in validation
        if step.get("name") == "Check changed changelog fragments"
    )
    assert "HEAD^1" in changelog["run"]
    assert "HEAD \\" in changelog["run"]
    assert "origin/main" not in changelog["run"]
    assert any(
        step.get("run") == "python .github/release_lock.py --rehearse"
        for step in validation
    )
    feedback = JOBS["Quick-Feedback"]["steps"]
    fetch = next(step for step in feedback if step.get("name") == "Fetch base branch")
    assert fetch["run"] == "git fetch origin ${{ github.base_ref }} --depth=1000"
    selective = next(
        step
        for step in feedback
        if step.get("name") == "Run selective tests based on changed files"
    )
    assert selective["env"]["GITHUB_BASE_REF"] == "${{ github.base_ref }}"
    assert "--base-branch ${{ github.base_ref }}" in selective["run"]
    for job in CHEAP_JOBS:
        assert "origin/main" not in str(JOBS[job])
    assert "Merge main" not in str(action("candidate-wheel"))
