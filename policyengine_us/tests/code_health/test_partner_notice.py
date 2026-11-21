"""Partner test changes reach Slack once a day per PR, threaded when possible.

.github/partner_notice.py decides each push's message; the Partner API impact
notice workflow runs it. These tests replace Slack with a recorder.
"""

from datetime import datetime, timedelta, timezone
import importlib.util
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[3]
WORKFLOW = REPO / ".github/workflows/partner-api-impact-notice.yaml"
SPEC = importlib.util.spec_from_file_location(
    "partner_notice", REPO / ".github/partner_notice.py"
)
notice = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(notice)

START = datetime(2026, 11, 20, 9, tzinfo=timezone.utc)
BOT = {"SLACK_PARTNER_BOT_TOKEN": "xoxb-test", "SLACK_PARTNER_CHANNEL_ID": "C1"}
WEBHOOK = {"SLACK_PARTNER_WEBHOOK_URL": "https://hooks.slack.test/T/B/X"}
PR = {
    "number": "11200",
    "title": "Raise <!channel> & SNAP",
    "url": "https://github.com/PolicyEngine/policyengine-us/pull/11200",
    "author": "contributor",
    "sha": "a" * 40,
}
A = "policyengine_us/tests/policy/baseline/partners/a.yaml"
B = "policyengine_us/tests/policy/baseline/partners/b.yaml"


class Slack:
    """Records messages; a bot message's timestamp names the push's commit."""

    def __init__(self, sha):
        self.sha = sha
        self.messages = []

    def __call__(self, text, thread_ts, env):
        self.messages.append((text, thread_ts))
        return f"ts-{self.sha[:1]}" if notice.threaded(env) else None


def push(state, files, env, now, sha="a"):
    slack = Slack(sha * 40)
    new_state = notice.notify(state, files, {**PR, "sha": sha * 40}, env, now, slack)
    return new_state, slack.messages


def test_a_bot_threads_every_push_within_a_day_then_starts_a_new_thread():
    state, (first,) = push(None, [A], BOT, START)
    assert first[1] is None and state["ts"] == "ts-a"
    assert "Pushes in the next 24 hours reply in this thread." in first[0]
    state, (reply,) = push(state, [A, B], BOT, START + timedelta(hours=23), "b")
    assert reply[1] == "ts-a"
    assert "Newly changed:" in reply[0] and B in reply[0]
    assert state["started"] == START.isoformat() and state["files"] == [A, B]
    state, (same,) = push(state, [A, B], BOT, START + timedelta(hours=23.5), "c")
    assert same[1] == "ts-a" and "The same partner files" in same[0]
    state, (later,) = push(state, [A, B], BOT, START + timedelta(hours=24), "d")
    assert later[1] is None and state["ts"] == "ts-d"
    assert state["started"] == (START + timedelta(hours=24)).isoformat()


def test_a_webhook_folds_pushes_unless_a_new_partner_file_appears_or_a_day_passes():
    state, (first,) = push(None, [A, B], WEBHOOK, START)
    assert state["ts"] is None
    assert "reply in this thread" not in first[0]
    assert push(state, [A], WEBHOOK, START + timedelta(hours=1)) == (None, [])
    assert push(state, [A, B], WEBHOOK, START + timedelta(hours=23)) == (None, [])
    later, (again,) = push(state, [A, B], WEBHOOK, START + timedelta(hours=24))
    assert later["started"] == (START + timedelta(hours=24)).isoformat()
    folded = {**state, "files": [A]}
    grown, (new,) = push(folded, [A, B], WEBHOOK, START + timedelta(hours=2))
    assert B in new[0] and grown["files"] == [A, B]


def test_a_new_bot_starts_a_thread_after_a_webhook_message():
    state, _ = push(None, [A], WEBHOOK, START)
    state, (first,) = push(state, [A], BOT, START + timedelta(hours=1), "b")
    assert first[1] is None and state["ts"] == "ts-b"


def test_no_credentials_post_nothing():
    assert push(None, [A], {}, START) == (None, [])


def test_titles_cannot_mention_or_link():
    text = notice.new_message(PR, [A], thread=True)
    assert "Raise &lt;!channel&gt; &amp; SNAP" in text
    assert "<!channel>" not in text


def test_long_file_lists_are_cut_at_twenty():
    files = [
        f"policyengine_us/tests/policy/baseline/partners/{i}.yaml" for i in range(25)
    ]
    text = notice.new_message(PR, files, thread=False)
    assert "Changed partner files: 25" in text
    assert text.count("\n- policyengine_us/") == 20
    assert "...and 5 more" in text


def test_the_workflow_runs_trusted_code_once_per_pr_at_a_time():
    workflow = yaml.safe_load(WORKFLOW.read_text())
    # PyYAML reads the bare `on` key as True.
    trigger = workflow[True]["pull_request_target"]
    assert trigger["paths"] == ["policyengine_us/tests/policy/baseline/partners/**"]
    assert workflow["concurrency"] == {
        "group": "partner-api-impact-notice-${{ github.event.pull_request.number }}",
        "cancel-in-progress": False,
    }
    assert workflow["permissions"] == {
        "actions": "read",
        "contents": "read",
        "pull-requests": "read",
    }
    (job,) = workflow["jobs"].values()
    for step in job["steps"]:
        # pull_request_target has secrets: never check out or run PR code, and
        # pass PR text through env, not into a shell command.
        assert "ref" not in step.get("with", {}), step["name"]
        assert "github.event.pull_request" not in step.get("run", ""), step["name"]
    (run,) = [
        step for step in job["steps"] if "partner_notice.py" in step.get("run", "")
    ]
    assert run["env"]["PR_TITLE"] == "${{ github.event.pull_request.title }}"
