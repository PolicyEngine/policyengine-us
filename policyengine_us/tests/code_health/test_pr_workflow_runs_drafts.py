"""Draft pull requests run the PR workflow as ready ones do, once per commit.

Drafts skipped CI while runners were short. With Enterprise runner capacity
they run it too, so authors see failures before asking for review.
"""

from pathlib import Path

import yaml

WORKFLOWS = Path(__file__).resolve().parents[3] / ".github" / "workflows"


def test_only_commit_events_trigger_the_workflow():
    data = yaml.safe_load((WORKFLOWS / "pr.yaml").read_text())
    # PyYAML reads the bare `on` key as True.
    trigger = data[True]["pull_request"]
    # Marking a draft ready, or a PR draft, leaves the commit unchanged, so a
    # run on either event would repeat the run its last push started.
    assert trigger["types"] == ["opened", "synchronize", "reopened"]


def test_no_job_or_step_depends_on_draft_state():
    for path in sorted(WORKFLOWS.glob("*.y*ml")):
        assert "pull_request.draft" not in path.read_text(), path.name
