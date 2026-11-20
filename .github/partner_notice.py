"""Tell Slack when a PR changes partner API contract tests, one thread a day.

The Partner API impact notice workflow runs this on each push to a PR that
changes policyengine_us/tests/policy/baseline/partners/**. Each run reads the
state the PR's previous run saved and returns the state for the next run.

- With SLACK_PARTNER_BOT_TOKEN and SLACK_PARTNER_CHANNEL_ID, the first push
  starts a thread and every push in the next 24 hours replies in it; a later
  push starts a new thread.
- With only SLACK_PARTNER_WEBHOOK_URL, which cannot reply in a thread, a push
  posts only when the last message is 24 hours old or the PR now changes a
  partner file that message did not list.

This helper uses only the standard library.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import sys
import urllib.request


WINDOW = timedelta(hours=24)
MAX_LISTED = 20
POST_MESSAGE = "https://slack.com/api/chat.postMessage"


def escape(text: str) -> str:
    """Slack reads &, < and > as entities, links and mentions."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def threaded(env: dict) -> bool:
    return bool(
        env.get("SLACK_PARTNER_BOT_TOKEN") and env.get("SLACK_PARTNER_CHANNEL_ID")
    )


def decide(state: dict | None, files: list[str], now: datetime, thread: bool) -> str:
    """new: start a message; reply: answer in its thread; skip: stay quiet."""
    if not state or now - datetime.fromisoformat(state["started"]) >= WINDOW:
        return "new"
    if thread:
        # A webhook message has no thread to reply in.
        return "reply" if state.get("ts") else "new"
    return "new" if set(files) - set(state["files"]) else "skip"


def listed(files: list[str]) -> list[str]:
    lines = [f"- {escape(file)}" for file in files[:MAX_LISTED]]
    if len(files) > MAX_LISTED:
        lines.append(f"- ...and {len(files) - MAX_LISTED} more in the PR's file diff.")
    return lines


def new_message(pr: dict, files: list[str], thread: bool) -> str:
    lines = [
        ":warning: Partner API contract tests changed",
        f"PR: <{pr['url']}|#{pr['number']} {escape(pr['title'])}>",
        f"Author: {escape(pr['author'])}",
        f"Changed partner files: {len(files)}",
        *listed(files),
        "",
        "Please review whether this changes partner-facing API behavior before merge.",
    ]
    if thread:
        lines.append("Pushes in the next 24 hours reply in this thread.")
    return "\n".join(lines)


def reply_message(pr: dict, files: list[str], previous: list[str]) -> str:
    added = sorted(set(files) - set(previous))
    removed = sorted(set(previous) - set(files))
    lines = [
        f"New commit <{pr['url']}/commits/{pr['sha']}|{pr['sha'][:7]}>: "
        f"{len(files)} partner files changed."
    ]
    if added:
        lines += ["Newly changed:", *listed(added)]
    if removed:
        lines += ["No longer changed:", *listed(removed)]
    if not added and not removed:
        lines.append("The same partner files as the last message.")
    return "\n".join(lines)


def post(url: str, payload: dict, token: str | None = None) -> str:
    headers = {"Content-Type": "application/json; charset=utf-8"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(
        url, data=json.dumps(payload).encode(), headers=headers
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode()


def send(text: str, thread_ts: str | None, env: dict) -> str | None:
    """Post a message and return its thread timestamp (None from a webhook)."""
    if not threaded(env):
        post(env["SLACK_PARTNER_WEBHOOK_URL"], {"text": text})
        return None
    payload = {
        "channel": env["SLACK_PARTNER_CHANNEL_ID"],
        "text": text,
        "unfurl_links": False,
    }
    if thread_ts:
        payload["thread_ts"] = thread_ts
    reply = json.loads(post(POST_MESSAGE, payload, env["SLACK_PARTNER_BOT_TOKEN"]))
    if not reply.get("ok"):
        raise RuntimeError(f"Slack rejected the message: {reply.get('error')}")
    return reply["ts"]


def notify(state, files, pr, env, now, send=send):
    """Post what this push needs and return the state to save, or None."""
    thread = threaded(env)
    if not thread and not env.get("SLACK_PARTNER_WEBHOOK_URL"):
        print("::notice::No Slack credentials are configured; skipping the notice.")
        return None
    action = decide(state, files, now, thread)
    if action == "skip":
        print("Folded into the last message: no new partner files within 24 hours.")
        return None
    if action == "reply":
        send(reply_message(pr, files, state["files"]), state["ts"], env)
        return {**state, "files": files, "sha": pr["sha"]}
    ts = send(new_message(pr, files, thread), None, env)
    return {"started": now.isoformat(), "ts": ts, "files": files, "sha": pr["sha"]}


def main(argv: list[str] | None = None, env: dict | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--files", required=True, help="the PR's partner files")
    parser.add_argument("--state", required=True, help="state file to read and write")
    args = parser.parse_args(argv)
    env = dict(os.environ) if env is None else env
    files = sorted(set(Path(args.files).read_text().split()))
    if not files:
        print("The PR changes no partner files.")
        return 0
    state_path = Path(args.state)
    state = json.loads(state_path.read_text()) if state_path.exists() else None
    pr = {
        "number": env["PR_NUMBER"],
        "title": env["PR_TITLE"],
        "url": env["PR_URL"],
        "author": env["PR_AUTHOR"],
        "sha": env["HEAD_SHA"],
    }
    new_state = notify(state, files, pr, env, datetime.now(timezone.utc))
    if new_state is not None:
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(json.dumps(new_state, indent=2) + "\n")
    if env.get("GITHUB_OUTPUT"):
        with open(env["GITHUB_OUTPUT"], "a") as output:
            output.write(f"saved={'true' if new_state is not None else 'false'}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
