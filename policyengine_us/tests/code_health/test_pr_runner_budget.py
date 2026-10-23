"""Consolidating short checks must preserve coverage and failure isolation."""

import math
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
JOBS = yaml.safe_load((ROOT / ".github/workflows/pr.yaml").read_text())["jobs"]
GROUP_WORKFLOWS = {
    name: yaml.safe_load((ROOT / job["uses"]).read_text())
    for name, job in JOBS.items()
    if "uses" in job
}
PYTHON_JOBS = GROUP_WORKFLOWS["PythonTests"]["jobs"]
PUSH_JOBS = yaml.safe_load((ROOT / ".github/workflows/push.yaml").read_text())["jobs"]
KEEP_RUNNING = "${{ !cancelled() }}"
KEEP_RUNNING_WITH_SYSTEM_CA = (
    "${{ !cancelled() && steps.system-ca.outcome == 'success' }}"
)


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


def runners(job):
    matrix = job.get("strategy", {}).get("matrix", {})
    if "include" in matrix:
        return len(matrix["include"])
    return math.prod(len(values) for values in matrix.values())


def test_pr_runner_budget_keeps_the_heavy_suites_separate():
    counts = {}
    runner_jobs = {name: job for name, job in JOBS.items() if "uses" not in job}
    for workflow in GROUP_WORKFLOWS.values():
        for name, job in workflow["jobs"].items():
            assert name not in runner_jobs
            runner_jobs[name] = job
    for name, job in runner_jobs.items():
        counts[name] = runners(job)
    # Rest hit the 90-minute timeout on #10024, #9913, #10139 and #10029
    # in October 2026. One extra runner buys about 45 minutes of headroom:
    # two tested shards share variables and the legacy summary check.
    assert sum(counts.values()) == 27
    assert {
        name: counts[name]
        for name in ("Baseline", "Contrib", "RestPython", "Rest", "Microsimulation")
    } == {
        "Baseline": 11,
        "Contrib": 9,
        "RestPython": 1,
        "Rest": 1,
        "Microsimulation": 1,
    }


def needs(job):
    value = job.get("needs", [])
    return [value] if isinstance(value, str) else value


def concurrent(job):
    return min(job.get("strategy", {}).get("max-parallel", math.inf), runners(job))


def test_uncapped_matrices_keep_a_pr_at_16_runners_at_once():
    # Within pr.yaml, validation runs alone; everything that needs only it starts
    # together, Rest waits for RestPython, and Contrib waits for Baseline.
    # The Enterprise runner capacity allows every group in each matrix to
    # start together. The existing dependencies still bound the peak.
    for name in ("Baseline", "Contrib"):
        for job in (GROUP_WORKFLOWS[name]["jobs"][name], PUSH_JOBS[name]):
            assert "max-parallel" not in job["strategy"]
    first_wave = {}
    for name, job in JOBS.items():
        if needs(job) != ["ReleaseLock"]:
            continue
        if "uses" not in job:
            first_wave[name] = concurrent(job)
            continue
        for inner_name, inner in GROUP_WORKFLOWS[name]["jobs"].items():
            if not needs(inner):
                first_wave[inner_name] = concurrent(inner)
    assert "Rest" not in first_wave and "Contrib" not in first_wave
    assert sum(first_wave.values()) == 16
    # Contrib starts only after Baseline has finished, so at most Contrib's
    # groups plus every other first-wave job can be running then.
    single = {name: n for name, n in first_wave.items() if name != "Baseline"}
    contrib = concurrent(GROUP_WORKFLOWS["Contrib"]["jobs"]["Contrib"])
    assert contrib + sum(single.values()) <= 16


def test_contrib_waits_for_baseline_and_skips_when_it_fails():
    # A plain needs (no if, or an if without a status function) skips Contrib
    # when Baseline fails or is cancelled. Re-running the failed Baseline group
    # then runs Contrib for the first time (fork run 38687143315); an if that
    # let Contrib run anyway would rerun all of its finished groups.
    assert needs(JOBS["Contrib"]) == ["ReleaseLock", "Baseline"]
    assert "if" not in JOBS["Contrib"]
    assert needs(PUSH_JOBS["Contrib"]) == ["ReleaseLock", "Baseline"]
    for status in ("always()", "cancelled()", "failure()", "success()"):
        assert status not in PUSH_JOBS["Contrib"]["if"]


def test_yaml_suites_run_two_memory_aware_workers_per_runner():
    for name in ("Baseline", "Contrib"):
        for job in (GROUP_WORKFLOWS[name]["jobs"][name], PUSH_JOBS[name]):
            assert job["env"]["POLICYENGINE_BATCH_WORKERS"] == 2


def test_release_ci_runs_the_same_baseline_and_contrib_matrices():
    for name in ("Baseline", "Contrib"):
        pr_job = GROUP_WORKFLOWS[name]["jobs"][name]
        assert PUSH_JOBS[name]["strategy"] == pr_job["strategy"]
        assert PUSH_JOBS[name]["steps"] == pr_job["steps"]
        assert PUSH_JOBS[name]["env"] == pr_job["env"]


def test_no_test_job_keeps_running_after_cancellation():
    # A job-level always() also holds after a manual or cancel-in-progress
    # cancellation, so the job keeps running or even starts after it. A job
    # that waits for another uses !cancelled() to run after its failure.
    workflows = {"pr.yaml": JOBS, "push.yaml": PUSH_JOBS} | {
        Path(job["uses"]).name: GROUP_WORKFLOWS[name]["jobs"]
        for name, job in JOBS.items()
        if "uses" in job
    }
    for file, jobs in workflows.items():
        for name, job in jobs.items():
            assert "always()" not in str(job.get("if", "")), (file, name)


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
            "needs": ["ReleaseLock", "Baseline"]
            if name == "Contrib"
            else "ReleaseLock",
            "uses": f"./.github/workflows/{file}",
        }
        # PyYAML parses the bare `on` key as True. No push/PR trigger here:
        # the draft guard must control the only route to these runners.
        assert GROUP_WORKFLOWS[name][True] == {"workflow_call": None}
    assert set(PYTHON_JOBS) == {"RestPython", "Rest", "Microsimulation"}
    assert {name: job["timeout-minutes"] for name, job in PYTHON_JOBS.items()} == {
        "RestPython": 90,
        "Rest": 90,
        "Microsimulation": 60,
    }
    for name, job in PYTHON_JOBS.items():
        assert job["runs-on"] == "ubuntu-latest"
        assert job.get("needs", []) == (["RestPython"] if name == "Rest" else [])
        assert not job.get("strategy")
        assert not job.get("continue-on-error")
    # The second tested runner also checks the first runner's result. There
    # is no third runner just for the summary, or a variables-only runner.
    # !cancelled(), not always(): always() kept it running after cancellation.
    assert PYTHON_JOBS["Rest"]["if"] == KEEP_RUNNING
    assert PYTHON_JOBS["Rest"]["name"] == "Full Suite - Rest (Python + variables)"


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
        assert all(step["if"] == KEEP_RUNNING_WITH_SYSTEM_CA for step in variants[1:])
        # A failure must remain a job failure even if a later variant passes.
        assert not JOBS[job].get("continue-on-error")
        assert all(
            not step.get("continue-on-error")
            for step in JOBS[job]["steps"] + action(name)
        )
    # A wheel failure must not suppress metadata or any Python version once
    # system trust setup succeeds. A failed trust check must stop every variant.
    checks = [
        step
        for step in JOBS["PackageCompatibility"]["steps"]
        if step.get("uses", "").startswith("./.github/actions/")
        and step["uses"] != "./.github/actions/setup-system-ca"
    ]
    assert len(checks) == 7
    # The first wheel keeps the implicit success() gate after trust setup.
    assert "if" not in checks[0]
    assert all(step["if"] == KEEP_RUNNING_WITH_SYSTEM_CA for step in checks[1:])


def test_package_variants_verify_system_trust_before_setting_up_environments():
    steps = JOBS["PackageCompatibility"]["steps"]
    (setup,) = calls("PackageCompatibility", "setup-system-ca")
    assert setup["id"] == "system-ca"
    assert "if" not in setup
    assert not setup.get("continue-on-error")
    assert steps[0]["uses"].startswith("actions/checkout@")
    assert steps[1] == setup


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
    assert call["if"] == KEEP_RUNNING_WITH_SYSTEM_CA
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
