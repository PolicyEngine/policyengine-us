"""Synchronize integration and open one immutable promotion at a time.

Uses only git, gh and the Python standard library; never imports the model.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
import os
import subprocess


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], check=True, capture_output=True, text=True
    ).stdout.strip()


def api(repository: str, resource: str, *, fields=None, paginate=False):
    command = ["gh", "api", f"repos/{repository}/{resource}"]
    if fields is not None:
        command.extend(["--method", "POST", "--input", "-"])
    if paginate:
        command.extend(["--paginate", "--slurp"])
    result = subprocess.run(
        command,
        input=json.dumps(fields) if fields is not None else None,
        check=True,
        capture_output=True,
        text=True,
    )
    data = json.loads(result.stdout)
    return [item for page in data for item in page] if paginate else data


def ancestor(older: str, newer: str) -> bool:
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", older, newer],
        capture_output=True,
        text=True,
    )
    if result.returncode not in (0, 1):
        result.check_returncode()
    return result.returncode == 0


def is_promotion(repository: str, pull: dict) -> bool:
    head = pull["head"]
    return (
        head["ref"].startswith("promote/")
        and (head.get("repo") or {}).get("full_name", "").lower() == repository.lower()
    )


def run(repository: str, now: datetime | None = None) -> None:
    if not git("ls-remote", "--heads", "origin", "refs/heads/integration"):
        print("::notice::Integration branch is absent; the pilot is inactive.")
        return
    git(
        "fetch",
        "--no-tags",
        "origin",
        "+refs/heads/main:refs/remotes/origin/main",
        "+refs/heads/integration:refs/remotes/origin/integration",
    )
    # Checking for an open promotion and creating one are separate API calls.
    # The workflow's constant concurrency group serializes scheduled and
    # dispatched runs so they cannot create competing snapshots.
    opened = api(repository, "pulls?state=open&base=main&per_page=100", paginate=True)
    for pull in opened:
        if is_promotion(repository, pull):
            print(f"::notice::Promotion #{pull['number']} is open; leaving it frozen.")
            return

    closed_promotions = api(
        repository, "pulls?state=closed&base=main&per_page=100", paginate=True
    )
    latest = max(
        (
            pull
            for pull in closed_promotions
            if pull.get("merged_at") and is_promotion(repository, pull)
        ),
        key=lambda pull: pull["merged_at"],
        default=None,
    )
    if latest and not ancestor(latest["head"]["sha"], "origin/main"):
        print(
            f"::error::Promotion #{latest['number']} was not merged with a merge "
            "commit and needs manual recovery before integration can be synchronized."
        )
        raise SystemExit(1)

    git("checkout", "-B", "integration", "origin/integration")
    if not ancestor("origin/main", "HEAD"):
        try:
            git("merge", "--no-edit", "origin/main")
        except subprocess.CalledProcessError as exc:
            git("merge", "--abort")
            print(exc.stdout or "")
            print(exc.stderr or "")
            print(
                "::warning::Main could not merge into integration. Resolve the "
                "conflict on integration before the next promotion."
            )
            return
        # A concurrent member merge rejects this ordinary push. Fail the tick
        # rather than overwrite it or create a snapshot from a stale head.
        git("push", "origin", "HEAD:refs/heads/integration")

    commits = git("rev-list", "--reverse", "origin/main..HEAD").splitlines()
    if not commits:
        print("::notice::Integration has no unpromoted commits; no promotion needed.")
        return
    closed = api(
        repository, "pulls?state=closed&base=integration&per_page=100", paginate=True
    )
    members = [
        pull
        for pull in closed
        if pull.get("merged_at") and pull.get("merge_commit_sha") in commits
    ]
    entries = git("log", "--reverse", "--format=%H%x09%s", "origin/main..HEAD")
    snapshot = git("rev-parse", "HEAD")
    good = git("rev-parse", "origin/main")
    stamp = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    branch = f"promote/{stamp:%Y%m%dT%H%M%S%fZ}"
    body = [
        f"Frozen integration snapshot: `{snapshot}`. Pre-batch main: `{good}`.",
        "",
        "Merge this PR with a **merge commit**, not squash or rebase, so each "
        "fix retains its commits and changelog fragments.",
        "",
        "Member PRs:",
    ]
    body.extend(f"- #{pull['number']}: {pull['title']}" for pull in members)
    if not members:
        body.append("- No associated merged integration PRs; see the commits below.")
    body.extend(["", "Member commits:"])
    for entry in entries.splitlines():
        sha, subject = entry.split("\t", 1)
        body.append(
            f"- [{sha[:12]}](https://github.com/{repository}/commit/{sha}) {subject}"
        )
    body.extend(
        [
            "",
            "If CI fails, follow CONTRIBUTING.md's red-promotion procedure. "
            "Close this PR after correcting integration, then dispatch Promote "
            "integration to cut a new snapshot.",
        ]
    )
    # Creating a ref rejects a name collision instead of moving a snapshot.
    api(repository, "git/refs", fields={"ref": f"refs/heads/{branch}", "sha": snapshot})
    pull = api(
        repository,
        "pulls",
        fields={
            "head": branch,
            "base": "main",
            "title": f"Promote integration ({stamp:%Y-%m-%d %H:%M:%S UTC})",
            "body": "\n".join(body),
            "draft": False,
        },
    )
    print(f"::notice::Created promotion {pull['html_url']}")


if __name__ == "__main__":
    try:
        run(os.environ["GITHUB_REPOSITORY"])
    except subprocess.CalledProcessError as exc:
        print(exc.stdout or "")
        print(exc.stderr or "")
        raise
