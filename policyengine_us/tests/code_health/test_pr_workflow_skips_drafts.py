"""Draft PRs skip every job; ready PRs run the tier selected by their base."""

from pathlib import Path

import yaml

WORKFLOW = Path(__file__).resolve().parents[3] / ".github" / "workflows" / "pr.yaml"
GUARD = "github.event.pull_request.draft == false"


def _workflow():
    data = yaml.safe_load(WORKFLOW.read_text())
    # PyYAML reads the bare `on` key as True.
    return data[True]["pull_request"], data["jobs"]


def _needs(job):
    needs = job.get("needs", [])
    return [needs] if isinstance(needs, str) else needs


def test_ready_for_review_and_converted_to_draft_trigger_the_workflow():
    trigger, _ = _workflow()
    assert set(trigger["branches"]) == {"main", "integration"}
    assert {"opened", "synchronize", "reopened", "ready_for_review"} <= set(
        trigger["types"]
    )
    # Converting back to draft starts a skipped run that cancels the old one.
    assert "converted_to_draft" in trigger["types"]


def test_every_job_is_skipped_for_drafts():
    _, jobs = _workflow()
    roots = [name for name, job in jobs.items() if not _needs(job)]
    assert roots, "the workflow must have at least one job without needs"
    for name in roots:
        assert jobs[name].get("if") == GUARD, name

    def reaches_guarded_root(name, seen=()):
        if name in seen:
            raise AssertionError(f"cycle at {name}")
        job = jobs[name]
        if not _needs(job):
            return job.get("if") == GUARD
        return all(reaches_guarded_root(n, seen + (name,)) for n in _needs(job))

    for name, job in jobs.items():
        # A job-level status function other than success() (always(),
        # !cancelled(), failure(), cancelled()) runs the job even when a
        # needed job was skipped, which would defeat the guard.
        condition = str(job.get("if", "")).replace(" ", "")
        for status_function in ("always()", "cancelled()", "failure()"):
            assert status_function not in condition, (name, condition)
        assert reaches_guarded_root(name), name
