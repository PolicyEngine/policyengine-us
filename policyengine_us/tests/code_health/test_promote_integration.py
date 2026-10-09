"""Exercise promotion orchestration with tiny Git repositories and no API writes."""

from datetime import datetime, timedelta, timezone
import importlib.util
import json
from pathlib import Path
import subprocess
from urllib.parse import parse_qs, urlsplit

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[3]
REPOSITORY = "PolicyEngine/policyengine-us"
NOW = datetime(2026, 10, 8, 20, 17, tzinfo=timezone.utc)


def command(path, *args):
    return subprocess.run(
        ["git", *args], cwd=path, capture_output=True, text=True, check=True
    ).stdout.strip()


class GitRepository:
    def __init__(self, root):
        self.remote = root / "remote.git"
        self.work = root / "work"
        command(root, "init", "--bare", "--initial-branch=main", str(self.remote))
        command(root, "clone", str(self.remote), str(self.work))
        self.configure(self.work)
        self.initial = self.commit("initial.txt", "initial", "Initial main")
        self.git("push", "origin", "main")

    @staticmethod
    def configure(path):
        command(path, "config", "user.name", "Promotion test")
        command(path, "config", "user.email", "promotion-test@example.com")

    def git(self, *args):
        return command(self.work, *args)

    def commit(self, name, contents, subject):
        (self.work / name).parent.mkdir(parents=True, exist_ok=True)
        (self.work / name).write_text(contents)
        self.git("add", name)
        self.git("commit", "-m", subject)
        return self.git("rev-parse", "HEAD")

    def integration(self):
        self.git("checkout", "-b", "integration")
        self.git("push", "origin", "integration")

    def publish_pull_head(self, number, snapshot):
        self.git("push", "origin", f"{snapshot}:refs/pull/{number}/head")

    def refs(self):
        output = command(
            self.remote, "for-each-ref", "--format=%(refname) %(objectname)"
        )
        return dict(line.split() for line in output.splitlines())


@pytest.fixture
def repository(tmp_path, monkeypatch):
    repository = GitRepository(tmp_path)
    monkeypatch.chdir(repository.work)
    return repository


@pytest.fixture
def promotion():
    spec = importlib.util.spec_from_file_location(
        "promote_integration", ROOT / ".github/promote_integration.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def api(monkeypatch, promotion, repository):
    class FakeAPI:
        def __init__(self):
            self.opened = []
            self.closed = []
            self.closed_main = []
            self.created = []
            self.queries = []
            self.writes = []

        def __call__(self, repository, resource, *, fields=None, paginate=False):
            assert repository == REPOSITORY
            if fields is not None:
                self.writes.append((resource, fields))
                assert not paginate
                if resource == "git/refs":
                    command(
                        local.remote,
                        "update-ref",
                        fields["ref"],
                        fields["sha"],
                        "0" * 40,
                    )
                    return {"ref": fields["ref"]}
                assert resource == "pulls"
                self.created.append(fields)
                return {"html_url": f"https://github.com/{REPOSITORY}/pull/123"}
            self.queries.append((resource, paginate))
            if "state=closed&base=main" in resource:
                assert not paginate
                query = parse_qs(urlsplit(resource).query)
                assert query == {
                    "state": ["closed"],
                    "base": ["main"],
                    "sort": ["updated"],
                    "direction": ["desc"],
                    "per_page": ["100"],
                    "page": query["page"],
                }
                page = int(query["page"][0])
                ordered = sorted(
                    self.closed_main, key=lambda pull: pull["updated_at"], reverse=True
                )
                return ordered[(page - 1) * 100 : page * 100]
            assert paginate, "Open and integration PR queries must read every page"
            if "state=open&base=main" in resource:
                return self.opened
            assert "state=closed&base=integration" in resource
            return self.closed

    local = repository
    fake = FakeAPI()
    monkeypatch.setattr(promotion, "api", fake)
    return fake


def closed_promotion(
    snapshot,
    *,
    number=42,
    merged_at="2026-10-08T12:00:00Z",
    updated_at=None,
):
    return {
        "number": number,
        "merged_at": merged_at,
        "updated_at": updated_at or merged_at or "2026-10-08T12:00:00Z",
        "head": {
            "ref": f"promote/{number}",
            "sha": snapshot,
            "repo": {"full_name": REPOSITORY},
        },
    }


def ordinary_pulls(count, updated_at, *, first_number=1000):
    pulls = [
        closed_promotion(
            "unused", number=first_number + index, updated_at=updated_at, merged_at=None
        )
        for index in range(count)
    ]
    for pull in pulls:
        pull["head"]["ref"] = "ordinary-fix"
    return pulls


def page_api(promotion, monkeypatch, pages):
    calls = []

    def api(repository, resource, *, paginate=False):
        assert repository == REPOSITORY
        assert not paginate
        page = len(calls) + 1
        assert resource == (
            "pulls?state=closed&base=main&sort=updated&direction=desc"
            f"&per_page=100&page={page}"
        )
        calls.append(resource)
        return pages[page - 1]

    monkeypatch.setattr(promotion, "api", api)
    return calls


def test_latest_promotion_stops_after_first_full_page(promotion, monkeypatch):
    candidate = closed_promotion("latest", updated_at="2026-10-08T13:00:00Z")
    pages = [
        [candidate, *ordinary_pulls(99, "2026-10-08T11:00:00Z")],
        [closed_promotion("older", number=41, merged_at="2026-10-07T12:00:00Z")],
    ]
    calls = page_api(promotion, monkeypatch, pages)
    assert promotion.latest_merged_promotion(REPOSITORY, set()) is candidate
    assert len(calls) == 1


def test_latest_promotion_can_be_on_third_page(promotion, monkeypatch):
    candidate = closed_promotion("latest")
    calls = page_api(
        promotion,
        monkeypatch,
        [
            ordinary_pulls(100, "2026-10-10T12:00:00Z"),
            ordinary_pulls(100, "2026-10-09T12:00:00Z", first_number=1100),
            [candidate],
        ],
    )
    assert promotion.latest_merged_promotion(REPOSITORY, set()) is candidate
    assert len(calls) == 3


def test_newer_update_does_not_hide_newest_merge_on_later_page(promotion, monkeypatch):
    older = closed_promotion(
        "older",
        number=41,
        merged_at="2026-10-07T12:00:00Z",
        updated_at="2026-10-10T12:00:00Z",
    )
    latest = closed_promotion("latest", updated_at="2026-10-08T13:00:00Z")
    calls = page_api(
        promotion,
        monkeypatch,
        [
            [older, *ordinary_pulls(99, "2026-10-09T12:00:00Z")],
            [latest],
        ],
    )
    assert promotion.latest_merged_promotion(REPOSITORY, set()) is latest
    assert len(calls) == 2


def test_no_promotion_reads_every_page_and_returns_none(promotion, monkeypatch):
    fork = closed_promotion("fork")
    fork["head"]["repo"]["full_name"] = "fork/repo"
    closed = closed_promotion("unmerged", number=43, merged_at=None)
    calls = page_api(
        promotion,
        monkeypatch,
        [
            ordinary_pulls(100, "2026-10-10T12:00:00Z"),
            ordinary_pulls(100, "2026-10-09T12:00:00Z", first_number=1100),
            [fork, closed],
        ],
    )
    assert promotion.latest_merged_promotion(REPOSITORY, set()) is None
    assert len(calls) == 3


def test_equal_update_boundary_continues_to_next_page(promotion, monkeypatch):
    candidate = closed_promotion("latest")
    calls = page_api(
        promotion,
        monkeypatch,
        [[candidate, *ordinary_pulls(99, candidate["merged_at"])], []],
    )
    assert promotion.latest_merged_promotion(REPOSITORY, set()) is candidate
    assert len(calls) == 2


def test_absent_integration_is_inert(repository, promotion, api, capsys):
    before = repository.refs()
    promotion.run(REPOSITORY, NOW)
    assert repository.refs() == before
    assert not api.queries
    assert not api.created
    assert "branch is absent" in capsys.readouterr().out


def test_two_ticks_without_new_commits_open_no_promotion(
    repository, promotion, api, capsys
):
    repository.integration()
    before = repository.refs()
    promotion.run(REPOSITORY, NOW)
    promotion.run(REPOSITORY, NOW + timedelta(hours=4))
    assert repository.refs() == before
    assert not api.created
    assert not api.writes
    assert len(api.queries) == 4
    assert "no unpromoted commits" in capsys.readouterr().out


def test_open_promotion_freezes_every_remote_ref(repository, promotion, api):
    repository.integration()
    frozen = repository.commit("fix.txt", "first", "First member fix")
    repository.git("push", "origin", "integration")
    repository.git("push", "origin", "HEAD:refs/heads/promote/existing")
    repository.commit("another.txt", "second", "Next batch member")
    repository.git("push", "origin", "integration")
    repository.git("checkout", "main")
    repository.commit("version.txt", "1.0.1", "Update PolicyEngine US")
    repository.git("push", "origin", "main")
    api.opened = [
        {
            "number": 42,
            "head": {"ref": "promote/existing", "repo": {"full_name": REPOSITORY}},
        }
    ]
    before = repository.refs()
    promotion.run(REPOSITORY, NOW)
    assert repository.refs() == before
    assert repository.refs()["refs/heads/promote/existing"] == frozen
    assert not api.created
    assert len(api.queries) == 1


def test_ready_batch_creates_non_draft_frozen_snapshot(repository, promotion, api):
    repository.integration()
    first = repository.commit("first.txt", "first", "First member fix")
    second = repository.commit("second.txt", "second", "Second member fix")
    repository.git("push", "origin", "integration")
    api.closed = [
        {
            "number": 101,
            "title": "First member fix",
            "merged_at": "2026-10-08T12:00:00Z",
            "merge_commit_sha": first,
        },
        {
            "number": 102,
            "title": "Unmerged PR is excluded",
            "merged_at": None,
            "merge_commit_sha": second,
        },
        {
            "number": 103,
            "title": "Previous batch is excluded",
            "merged_at": "2026-10-07T12:00:00Z",
            "merge_commit_sha": repository.initial,
        },
    ]
    # A branch with the same prefix in a fork does not block this repository.
    api.opened = [
        {
            "number": 99,
            "head": {"ref": "promote/fork", "repo": {"full_name": "fork/repo"}},
        }
    ]
    promotion.run(REPOSITORY, NOW)
    assert not api.closed_main
    assert (
        "pulls?state=closed&base=main&sort=updated&direction=desc&per_page=100&page=1",
        False,
    ) in api.queries
    (pull,) = api.created
    assert pull["head"] == "promote/20261008T201700000000Z"
    assert pull["base"] == "main"
    assert pull["draft"] is False
    assert pull["title"].startswith("Promote integration")
    assert repository.refs()[f"refs/heads/{pull['head']}"] == second
    body = pull["body"]
    assert first in body and second in body and repository.initial in body
    assert body.index("First member fix", body.index("Member commits:")) < body.index(
        "Second member fix", body.index("Member commits:")
    )
    assert "#101: First member fix" in body
    assert "#102" not in body and "#103" not in body
    assert "**merge commit**" in body
    repository.commit("later.txt", "later", "Next integration batch")
    repository.git("push", "origin", "integration")
    assert repository.refs()[f"refs/heads/{pull['head']}"] == second


def test_closed_unmerged_promotion_allows_a_fresh_snapshot(repository, promotion, api):
    repository.integration()
    snapshot = repository.commit("fix.txt", "fix", "Member fix")
    repository.git("push", "origin", "integration")
    promotion.run(REPOSITORY, NOW)
    (first,) = api.created
    closed = closed_promotion(snapshot, merged_at=None)
    closed["head"]["ref"] = first["head"]
    api.closed_main = [closed]
    promotion.run(REPOSITORY, NOW + timedelta(hours=4))
    assert len(api.created) == 2
    second = api.created[1]
    assert first["head"] != second["head"]
    refs = repository.refs()
    assert refs[f"refs/heads/{first['head']}"] == snapshot
    assert refs[f"refs/heads/{second['head']}"] == snapshot
    assert refs["refs/heads/integration"] == snapshot


@pytest.mark.parametrize("method", ["squash", "rebase"])
def test_rewritten_promotion_fails_before_sync_push_or_api_writes(
    repository, promotion, api, monkeypatch, capsys, method
):
    repository.integration()
    snapshot = repository.commit("fix.txt", "fix", "Promoted fix")
    repository.git("push", "origin", "integration")
    repository.publish_pull_head(42, snapshot)
    repository.git("checkout", "main")
    if method == "squash":
        repository.git("merge", "--squash", "integration")
        repository.git("commit", "-m", "Squash promotion")
    else:
        # Replaying on newer main gives the member a different parent and SHA.
        repository.commit("main.txt", "main", "New main fix")
        repository.git("cherry-pick", snapshot)
    repository.commit("version.txt", "1.0.1", "Update PolicyEngine US")
    repository.git("push", "origin", "main")
    latest = closed_promotion(snapshot)
    fork = closed_promotion(snapshot, number=99, merged_at="2026-10-09T12:00:00Z")
    fork["head"]["repo"]["full_name"] = "fork/repo"
    ordinary = closed_promotion(snapshot, number=100, merged_at="2026-10-09T12:00:00Z")
    ordinary["head"]["ref"] = "ordinary-fix"
    api.closed_main = [
        latest,
        closed_promotion(
            repository.initial, number=41, merged_at="2026-10-07T12:00:00Z"
        ),
        fork,
        ordinary,
        closed_promotion(snapshot, number=101, merged_at=None),
    ]
    before = repository.refs()
    calls = []
    original_git = promotion.git

    def tracked_git(*args):
        calls.append(args)
        return original_git(*args)

    monkeypatch.setattr(promotion, "git", tracked_git)
    with pytest.raises(SystemExit) as exc:
        promotion.run(REPOSITORY, NOW)
    assert exc.value.code == 1
    assert repository.refs() == before
    assert not any(args[0] in {"checkout", "merge", "push"} for args in calls)
    assert not api.writes
    assert not api.created
    output = capsys.readouterr().out
    assert "::error::Promotion #42" in output
    assert "was not merged with a merge commit" in output
    assert "needs manual recovery" in output


def test_unfetchable_promotion_head_reports_error_before_any_writes(
    repository, promotion, api, monkeypatch, capsys
):
    repository.integration()
    repository.commit("fix.txt", "fix", "Unpromoted fix")
    repository.git("push", "origin", "integration")
    repository.git("checkout", "main")
    repository.commit("main.txt", "main", "New main fix")
    repository.git("push", "origin", "main")
    api.closed_main = [closed_promotion("f" * 40)]
    before = repository.refs()
    calls = []
    original_git = promotion.git

    def tracked_git(*args):
        calls.append(args)
        return original_git(*args)

    monkeypatch.setattr(promotion, "git", tracked_git)
    with pytest.raises(SystemExit) as exc:
        promotion.run(REPOSITORY, NOW)
    assert exc.value.code == 1
    assert (
        "fetch",
        "--no-tags",
        "origin",
        "+refs/pull/42/head:refs/remotes/origin/promotion-head",
    ) in calls
    assert not any(args[0] in {"checkout", "merge", "push"} for args in calls)
    assert repository.refs() == before
    assert not api.created
    assert not api.writes
    output = capsys.readouterr().out
    assert "::error::Cannot verify promotion #42" in output
    assert "refs/pull/42/head" in output


def test_ancestry_error_reports_promotion_instead_of_unhandled_exception(
    repository, promotion, api, monkeypatch, capsys
):
    repository.integration()
    snapshot = repository.commit("fix.txt", "fix", "Promoted fix")
    repository.git("push", "origin", "integration")
    repository.publish_pull_head(42, snapshot)
    api.closed_main = [closed_promotion(snapshot)]
    before = repository.refs()

    def broken_ancestor(older, newer):
        assert (older, newer) == ("origin/promotion-head", "origin/main")
        raise subprocess.CalledProcessError(
            128,
            ["git", "merge-base", "--is-ancestor", older, newer],
            stderr="fatal: unable to read tree object\n",
        )

    monkeypatch.setattr(promotion, "ancestor", broken_ancestor)
    with pytest.raises(SystemExit) as exc:
        promotion.run(REPOSITORY, NOW)
    assert exc.value.code == 1
    assert repository.refs() == before
    assert not api.created
    assert not api.writes
    output = capsys.readouterr().out
    assert "::error::Cannot verify promotion #42" in output
    assert "fatal: unable to read tree object" in output


def test_recovered_promotion_file_is_read_from_main_with_comments(
    repository, promotion
):
    repository.commit(
        ".github/promotion-recovered.txt",
        "# Reconciled promotions\n42\n\n  41  # Older repaired batch\n",
        "Acknowledge repaired promotions",
    )
    repository.git("push", "origin", "main")
    # An uncommitted local file cannot acknowledge recovery for the guard.
    (repository.work / ".github/promotion-recovered.txt").write_text("99\n")
    assert promotion.recovered_promotions() == {41, 42}


def test_missing_recovery_file_is_empty(repository, promotion):
    assert promotion.recovered_promotions() == set()


def test_acknowledged_squash_allows_repaired_integration_to_run(
    repository, promotion, api, capsys
):
    repository.integration()
    snapshot = repository.commit("fix.txt", "fix", "Promoted fix")
    repository.git("push", "origin", "integration")
    repository.publish_pull_head(42, snapshot)
    repository.git("checkout", "main")
    repository.git("merge", "--squash", "integration")
    repository.git("commit", "-m", "Squash promotion")
    repository.commit(
        ".github/promotion-recovered.txt",
        "# Reconciled promotions\n42\n",
        "Recover #42",
    )
    repository.git("push", "origin", "main")
    repository.git("checkout", "integration")
    repository.git("reset", "--hard", "main")
    repository.git("push", "--force", "origin", "integration")
    api.closed_main = [closed_promotion(snapshot)]
    before = repository.refs()
    promotion.run(REPOSITORY, NOW)
    assert repository.refs() == before
    assert not api.created
    assert not api.writes
    assert "no unpromoted commits" in capsys.readouterr().out


def test_acknowledged_squash_does_not_hide_older_unreconciled_squash(
    repository, promotion, api, capsys
):
    repository.integration()
    older = repository.commit("older.txt", "older", "Older promoted fix")
    repository.git("push", "origin", "integration")
    repository.publish_pull_head(41, older)
    repository.git("checkout", "main")
    repository.git("merge", "--squash", "integration")
    repository.git("commit", "-m", "Squash older promotion")
    repository.git("checkout", "integration")
    repository.git("reset", "--hard", "main")
    latest = repository.commit("latest.txt", "latest", "Latest promoted fix")
    repository.git("push", "--force", "origin", "integration")
    repository.publish_pull_head(42, latest)
    repository.git("checkout", "main")
    repository.git("merge", "--squash", "integration")
    repository.git("commit", "-m", "Squash latest promotion")
    repository.commit(
        ".github/promotion-recovered.txt", "42\n", "Acknowledge latest repaired batch"
    )
    repository.git("push", "origin", "main")
    repository.git("checkout", "integration")
    repository.git("reset", "--hard", "main")
    repository.git("push", "--force", "origin", "integration")
    api.closed_main = [
        closed_promotion(latest),
        closed_promotion(older, number=41, merged_at="2026-10-07T12:00:00Z"),
    ]
    before = repository.refs()
    with pytest.raises(SystemExit) as exc:
        promotion.run(REPOSITORY, NOW)
    assert exc.value.code == 1
    assert repository.refs() == before
    assert not api.created
    assert not api.writes
    output = capsys.readouterr().out
    assert "::error::Promotion #41" in output
    assert "needs manual recovery" in output


def test_existing_snapshot_ref_is_never_advanced(repository, promotion, api):
    repository.integration()
    frozen = repository.commit("first.txt", "first", "First member")
    branch = "promote/20261008T201700000000Z"
    repository.git("push", "origin", f"HEAD:refs/heads/{branch}")
    repository.commit("second.txt", "second", "Second member")
    repository.git("push", "origin", "integration")
    before = repository.refs()
    with pytest.raises(subprocess.CalledProcessError):
        promotion.run(REPOSITORY, NOW)
    assert repository.refs() == before
    assert repository.refs()[f"refs/heads/{branch}"] == frozen
    assert not api.created


def test_promoted_integration_receives_version_bump_without_new_pr(
    repository, promotion, api
):
    repository.integration()
    snapshot = repository.commit("fix.txt", "fix", "Promoted fix")
    repository.git("push", "origin", "integration")
    repository.publish_pull_head(42, snapshot)
    repository.git("checkout", "main")
    repository.git("merge", "--no-ff", "integration", "-m", "Merge promotion")
    bumped = repository.commit("version.txt", "1.0.1", "Update PolicyEngine US")
    repository.git("push", "origin", "main")
    # Update order is unrelated to merge order; the latest promotion's head is
    # preserved in main even though the more recently updated older one is not.
    unrelated = repository.commit("unused.txt", "unused", "Unmerged local commit")
    api.closed_main = [
        closed_promotion(
            unrelated,
            number=41,
            merged_at="2026-10-07T12:00:00Z",
            updated_at="2026-10-09T12:00:00Z",
        ),
        closed_promotion(snapshot),
    ]
    promotion.run(REPOSITORY, NOW)
    assert repository.refs()["refs/heads/integration"] == bumped
    assert not api.created
    assert not api.writes
    assert len(api.queries) == 2


def test_new_member_after_promotion_preserves_main_and_member_commits(
    repository, promotion, api
):
    repository.integration()
    repository.commit("old.txt", "old", "Previous batch fix")
    repository.git("push", "origin", "integration")
    repository.git("checkout", "main")
    repository.git("merge", "--no-ff", "integration", "-m", "Merge promotion")
    bumped = repository.commit("version.txt", "1.0.1", "Update PolicyEngine US")
    repository.git("push", "origin", "main")
    repository.git("checkout", "integration")
    member = repository.commit("new.txt", "new", "Next batch fix")
    repository.git("push", "origin", "integration")
    promotion.run(REPOSITORY, NOW)
    (pull,) = api.created
    snapshot = repository.refs()[f"refs/heads/{pull['head']}"]
    assert repository.refs()["refs/heads/integration"] == snapshot
    assert promotion.ancestor(bumped, snapshot)
    assert promotion.ancestor(member, snapshot)
    assert (repository.work / "version.txt").read_text() == "1.0.1"
    assert member in pull["body"]


def test_merge_conflict_leaves_remote_untouched_and_reports_resolution(
    repository, promotion, api, capsys
):
    repository.integration()
    repository.commit("initial.txt", "integration", "Member change")
    repository.git("push", "origin", "integration")
    repository.git("checkout", "main")
    repository.commit("initial.txt", "main", "Main change")
    repository.git("push", "origin", "main")
    before = repository.refs()
    promotion.run(REPOSITORY, NOW)
    assert repository.refs() == before
    assert not api.created
    assert not repository.git("status", "--porcelain")
    assert "Resolve the conflict on integration" in capsys.readouterr().out


def test_concurrent_member_push_rejects_stale_sync_without_promotion(
    repository, promotion, api, monkeypatch
):
    repository.integration()
    repository.commit("member.txt", "first", "First member")
    repository.git("push", "origin", "integration")
    repository.git("checkout", "main")
    repository.commit("main.txt", "main", "Urgent main fix")
    repository.git("push", "origin", "main")
    other = repository.work.parent / "other"
    command(other.parent, "clone", str(repository.remote), str(other))
    repository.configure(other)
    command(other, "checkout", "integration")
    (other / "race.txt").write_text("concurrent member")
    command(other, "add", "race.txt")
    command(other, "commit", "-m", "Concurrent member")
    concurrent = command(other, "rev-parse", "HEAD")
    original_git = promotion.git

    def racing_git(*args):
        if args == ("push", "origin", "HEAD:refs/heads/integration"):
            command(other, "push", "origin", "integration")
        return original_git(*args)

    monkeypatch.setattr(promotion, "git", racing_git)
    with pytest.raises(subprocess.CalledProcessError):
        promotion.run(REPOSITORY, NOW)
    assert repository.refs()["refs/heads/integration"] == concurrent
    assert not any(ref.startswith("refs/heads/promote/") for ref in repository.refs())
    assert not api.created


def test_api_pagination_keeps_promotions_from_later_pages(promotion, monkeypatch):
    pages = [[{"number": 1}], [{"number": 2}]]
    calls = []

    def run(args, **kwargs):
        calls.append((args, kwargs))
        return subprocess.CompletedProcess(args, 0, stdout=json.dumps(pages))

    monkeypatch.setattr(promotion.subprocess, "run", run)
    assert promotion.api(REPOSITORY, "pulls?state=open", paginate=True) == [
        {"number": 1},
        {"number": 2},
    ]
    ((args, kwargs),) = calls
    assert args == [
        "gh",
        "api",
        f"repos/{REPOSITORY}/pulls?state=open",
        "--paginate",
        "--slurp",
    ]
    assert kwargs["check"]


def test_api_posts_draft_as_a_json_boolean(promotion, monkeypatch):
    calls = []

    def run(args, **kwargs):
        calls.append((args, kwargs))
        return subprocess.CompletedProcess(args, 0, stdout='{"number": 123}')

    monkeypatch.setattr(promotion.subprocess, "run", run)
    fields = {"head": "promote/snapshot", "base": "main", "draft": False}
    assert promotion.api(REPOSITORY, "pulls", fields=fields) == {"number": 123}
    ((args, kwargs),) = calls
    assert args == [
        "gh",
        "api",
        f"repos/{REPOSITORY}/pulls",
        "--method",
        "POST",
        "--input",
        "-",
    ]
    assert json.loads(kwargs["input"]) == fields


def test_promotion_workflow_keeps_token_gate_and_bounded_schedule():
    workflow = yaml.safe_load(
        (ROOT / ".github/workflows/promote-integration.yaml").read_text()
    )
    push = yaml.safe_load((ROOT / ".github/workflows/push.yaml").read_text())
    assert push[True] == {"push": {"branches": ["main"]}}
    assert workflow[True] == {
        "schedule": [{"cron": "17 */4 * * *"}],
        "workflow_dispatch": None,
    }
    assert workflow["permissions"] == {"contents": "read"}
    assert workflow["concurrency"] == {
        "group": "promote-integration",
        "cancel-in-progress": False,
    }
    assert set(workflow["jobs"]) == {"promote"}
    job = workflow["jobs"]["promote"]
    assert job["timeout-minutes"] == 10
    assert job["if"] == "github.repository == 'PolicyEngine/policyengine-us'"
    steps = job["steps"]
    pilot = next(step for step in steps if step.get("id") == "pilot")
    token = next(step for step in steps if step.get("id") == "app-token")
    push_token = next(
        step
        for step in push["jobs"]["versioning"]["steps"]
        if step.get("id") == "app-token"
    )
    assert token["uses"] == push_token["uses"]
    assert token["with"] == {
        **push_token["with"],
        "permission-contents": "write",
        "permission-pull-requests": "write",
        "permission-workflows": "write",
    }
    assert "git ls-remote --heads origin refs/heads/integration" in pilot["run"]
    assert steps.index(pilot) < steps.index(token)
    gate = "steps.pilot.outputs.enabled == 'true'"
    assert all(step["if"] == gate for step in steps[steps.index(token) :])
    run = steps[-1]
    assert run["env"]["GH_TOKEN"] == "${{ steps.app-token.outputs.token }}"
    checkout = steps[-2]
    assert checkout["with"]["token"] == "${{ steps.app-token.outputs.token }}"
    assert checkout["with"]["fetch-depth"] == 0
