import json
import os
from pathlib import Path
import subprocess
from unittest.mock import patch

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
import pytest

from policyengine_us import build_metadata
from policyengine_us.build_metadata import (
    get_data_build_fingerprint,
    get_data_build_metadata,
    get_runtime_metadata,
)


def test_data_build_fingerprint_is_stable_within_process():
    get_data_build_fingerprint.cache_clear()

    first = get_data_build_fingerprint()
    second = get_data_build_fingerprint()

    assert first.startswith("sha256:")
    assert first == second


def test_get_runtime_metadata_includes_version_git_sha_fingerprint_and_core():
    get_data_build_fingerprint.cache_clear()

    with (
        patch(
            "policyengine_us.build_metadata._get_package_version",
            return_value="1.602.0",
        ),
        patch(
            "policyengine_us.build_metadata._get_git_sha",
            return_value="deadbeef",
        ),
        patch(
            "policyengine_us.build_metadata.get_data_build_fingerprint",
            return_value="sha256:fingerprint",
        ),
        patch(
            "policyengine_us.build_metadata.get_core_runtime_metadata",
            return_value={
                "name": "policyengine-core",
                "version": "3.26.0",
                "git_sha": "coredeadbeef",
            },
        ),
    ):
        metadata = get_runtime_metadata()

    assert metadata == {
        "name": "policyengine-us",
        "version": "1.602.0",
        "git_sha": "deadbeef",
        "data_build_fingerprint": "sha256:fingerprint",
        "core": {
            "name": "policyengine-core",
            "version": "3.26.0",
            "git_sha": "coredeadbeef",
        },
    }


def test_get_data_build_metadata_uses_runtime_metadata():
    with patch(
        "policyengine_us.build_metadata.get_runtime_metadata",
        return_value={"name": "policyengine-us"},
    ):
        assert get_data_build_metadata() == {"name": "policyengine-us"}


def test_runtime_metadata_uses_bundle_contract_when_available():
    policyengine_bundles = pytest.importorskip("policyengine_bundles")

    policyengine_bundles.load_component_metadata(get_runtime_metadata())


# _get_git_sha must return policyengine-us's own commit or None, never the HEAD
# of a repository that merely contains the install.

_get_git_sha = build_metadata._get_git_sha
_get_direct_url_git_sha = build_metadata._get_direct_url_git_sha

# The tests' own git calls must not be redirected by the caller's environment
# or shaped by the user's git configuration.
GIT_TEST_ENV = {
    **{
        key: value
        for key, value in os.environ.items()
        if key not in build_metadata.GIT_REPOSITORY_ENV_VARS
    },
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_NOSYSTEM": "1",
}
SHA = "0123456789abcdef0123456789abcdef01234567"
SITE_PACKAGES = ".venv/lib/python3.13/site-packages"


def _git(cwd: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(cwd), *args],
        env=GIT_TEST_ENV,
        stderr=subprocess.DEVNULL,
        text=True,
    ).strip()


def _commit(repo: Path, message: str) -> str:
    _git(repo, "add", "-A")
    _git(
        repo,
        "-c",
        "user.name=Test",
        "-c",
        "user.email=test@example.com",
        "commit",
        "-q",
        "--allow-empty",
        "-m",
        message,
    )
    return _git(repo, "rev-parse", "HEAD")


def _init_repo(repo: Path, project_name: str | None) -> str:
    """Create a git repository with one commit and return its HEAD."""
    repo.mkdir(parents=True, exist_ok=True)
    _git(repo, "init", "-q")
    if project_name is not None:
        (repo / "pyproject.toml").write_text(f'[project]\nname = "{project_name}"\n')
    # The message keeps commits in different repositories distinct.
    return _commit(repo, str(repo))


def _make_package(parent: Path) -> Path:
    package_root = parent / "policyengine_us"
    package_root.mkdir(parents=True, exist_ok=True)
    (package_root / "__init__.py").write_text("")
    return package_root


def _make_policyengine_us_checkout(checkout: Path) -> tuple[Path, str]:
    package_root = _make_package(checkout)
    return package_root, _init_repo(checkout, "policyengine-us")


def _install_with_direct_url(site_packages: Path, direct_url: object) -> Path:
    """Lay out an installed policyengine-us with an installer record."""
    package_root = _make_package(site_packages)
    dist_info = site_packages / "policyengine_us-2.0.0.dist-info"
    dist_info.mkdir()
    (dist_info / "METADATA").write_text(
        "Metadata-Version: 2.1\nName: policyengine-us\nVersion: 2.0.0\n"
    )
    if direct_url is not None:
        (dist_info / "direct_url.json").write_text(
            direct_url if isinstance(direct_url, str) else json.dumps(direct_url)
        )
    return package_root


def test_git_sha_ignores_enclosing_repository(tmp_path):
    # A data build: policyengine-us installed into a virtualenv inside the
    # data repository's checkout, as in PolicyEngine/microcosm.
    microcosm = tmp_path / "microcosm"
    _init_repo(microcosm, "microcosm-workspace")
    package_root = _make_package(microcosm / SITE_PACKAGES)

    assert _get_git_sha(package_root) is None


def test_git_sha_ignores_enclosing_policyengine_us_checkout(tmp_path):
    # A non-editable install can be built from any commit, so the HEAD of a
    # policyengine-us checkout that holds the virtualenv is not evidence.
    checkout = tmp_path / "policyengine-us"
    _init_repo(checkout, "policyengine-us")
    package_root = _make_package(checkout / SITE_PACKAGES)

    assert _get_git_sha(package_root) is None


@pytest.mark.parametrize("project_name", ["deployment", None])
def test_git_sha_ignores_repository_that_vendors_the_package(tmp_path, project_name):
    # For example `pip install --target .` at the root of another repository.
    repo = tmp_path / "deployment"
    package_root = _make_package(repo)
    _init_repo(repo, project_name)

    assert _get_git_sha(package_root) is None


def test_git_sha_ignores_unusable_git_directory(tmp_path):
    # Git skips an empty .git directory and finds the enclosing repository.
    outer = tmp_path / "outer"
    _init_repo(outer, "outer")
    checkout = outer / "policyengine-us"
    package_root = _make_package(checkout)
    (checkout / ".git").mkdir()
    (checkout / "pyproject.toml").write_text('[project]\nname = "policyengine-us"\n')

    assert _get_git_sha(package_root) is None


def test_git_sha_ignores_malformed_pyproject(tmp_path):
    checkout = tmp_path / "policyengine-us"
    package_root, _ = _make_policyengine_us_checkout(checkout)
    (checkout / "pyproject.toml").write_text("[project\n")

    assert _get_git_sha(package_root) is None


def test_git_sha_reads_own_checkout_head(tmp_path):
    package_root, head = _make_policyengine_us_checkout(tmp_path / "policyengine-us")

    assert _get_git_sha(package_root) == head


def test_git_sha_reads_own_checkout_nested_in_another_repository(tmp_path):
    outer = tmp_path / "microcosm"
    outer_head = _init_repo(outer, "microcosm-workspace")
    package_root, head = _make_policyengine_us_checkout(
        outer / "vendor" / "policyengine-us"
    )

    assert _get_git_sha(package_root) == head
    assert head != outer_head


def test_git_sha_reads_own_worktree_head(tmp_path):
    main = tmp_path / "policyengine-us"
    _, main_head = _make_policyengine_us_checkout(main)
    worktree = tmp_path / "policyengine-us-feature"
    _git(main, "worktree", "add", "-q", "-b", "feature", str(worktree))
    worktree_head = _commit(worktree, "feature")

    assert (worktree / ".git").is_file()
    assert _get_git_sha(worktree / "policyengine_us") == worktree_head
    assert worktree_head != main_head


def test_git_sha_ignores_git_environment_overrides(tmp_path, monkeypatch):
    outer = tmp_path / "outer"
    _init_repo(outer, "outer")
    package_root, head = _make_policyengine_us_checkout(tmp_path / "policyengine-us")
    monkeypatch.setenv("GIT_DIR", str(outer / ".git"))
    monkeypatch.setenv("GIT_WORK_TREE", str(outer))

    assert _get_git_sha(package_root) == head


def test_git_sha_is_none_before_first_commit(tmp_path):
    checkout = tmp_path / "policyengine-us"
    package_root = _make_package(checkout)
    _git(checkout, "init", "-q")
    (checkout / "pyproject.toml").write_text('[project]\nname = "policyengine-us"\n')

    assert _get_git_sha(package_root) is None


def test_git_sha_is_none_without_git_executable(tmp_path, monkeypatch):
    package_root, _ = _make_policyengine_us_checkout(tmp_path / "policyengine-us")

    def missing_git(*args, **kwargs):
        raise FileNotFoundError("git")

    monkeypatch.setattr(build_metadata.subprocess, "check_output", missing_git)

    assert _get_git_sha(package_root) is None


def test_git_sha_reads_this_checkout_head():
    try:
        toplevel = Path(
            _git(build_metadata.PACKAGE_ROOT, "rev-parse", "--show-toplevel")
        )
    except (OSError, subprocess.CalledProcessError):
        pytest.skip("policyengine-us is not running from a git checkout")
    if not build_metadata._declares_package(toplevel / "pyproject.toml"):
        pytest.skip("the enclosing git checkout is not policyengine-us")
    if not os.path.samefile(toplevel, build_metadata.PACKAGE_ROOT.parent):
        pytest.skip("policyengine-us is installed inside its checkout, not run from it")

    assert _get_git_sha() == _git(toplevel, "rev-parse", "HEAD")


def test_git_sha_reads_installer_record_for_git_install(tmp_path):
    package_root = _install_with_direct_url(
        tmp_path / "site-packages",
        {
            "url": "https://github.com/PolicyEngine/policyengine-us",
            "vcs_info": {"vcs": "git", "commit_id": SHA},
        },
    )

    assert _get_git_sha(package_root) == SHA


def test_git_sha_prefers_installer_record_over_enclosing_repository(tmp_path):
    microcosm = tmp_path / "microcosm"
    _init_repo(microcosm, "microcosm-workspace")
    package_root = _install_with_direct_url(
        microcosm / SITE_PACKAGES,
        {"url": "https://example.com", "vcs_info": {"vcs": "git", "commit_id": SHA}},
    )

    assert _get_git_sha(package_root) == SHA


@pytest.mark.parametrize(
    "direct_url",
    [
        None,
        "not json",
        [],
        {"url": "file:///src/policyengine-us", "dir_info": {"editable": True}},
        {"url": "https://example.com/policyengine_us.whl", "archive_info": {}},
        {"url": "https://example.com", "vcs_info": {"vcs": "hg", "commit_id": SHA}},
        {"url": "https://example.com", "vcs_info": {"vcs": "git"}},
        {"url": "https://example.com", "vcs_info": {"vcs": "git", "commit_id": "main"}},
        {"url": "https://example.com", "vcs_info": "git"},
    ],
)
def test_git_sha_ignores_installer_records_without_git_commit(tmp_path, direct_url):
    package_root = _install_with_direct_url(tmp_path / "site-packages", direct_url)

    assert _get_git_sha(package_root) is None


def test_git_sha_ignores_installer_record_of_another_copy(tmp_path):
    _install_with_direct_url(
        tmp_path / "other-site-packages",
        {"url": "https://example.com", "vcs_info": {"vcs": "git", "commit_id": SHA}},
    )
    package_root = _make_package(tmp_path / "site-packages")

    assert _get_git_sha(package_root) is None


def test_runtime_metadata_git_sha_is_none_or_a_commit():
    # Whatever this test run's install layout is, the reported sha is either
    # unknown or a full commit id, and looking it up does not raise.
    git_sha = get_runtime_metadata()["git_sha"]

    assert git_sha is None or build_metadata.GIT_SHA_PATTERN.fullmatch(git_sha)


# Property: for any directory layout, the sha is the HEAD of a repository
# rooted at the package's parent whose pyproject names policyengine-us, or None.

PATH_SEGMENTS = st.one_of(
    st.sampled_from(
        [
            ".venv",
            "venv",
            "lib",
            "python3.13",
            "site-packages",
            "dist-packages",
            "src",
            "vendor",
            "build",
            "policyengine-us",
            "policyengine_us",
        ]
    ),
    # No dots, so a segment can never be ".git", "." or "pyproject.toml".
    st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789-_", min_size=1, max_size=8),
)
PROPERTY_SETTINGS = settings(
    max_examples=40,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow],
)


@PROPERTY_SETTINGS
@given(
    project_name=st.sampled_from(
        [None, "policyengine-us", "policyengine_us", "microcosm-workspace"]
    ),
    segments=st.lists(PATH_SEGMENTS, max_size=4),
)
def test_git_sha_property_only_own_checkout_root(
    tmp_path_factory, project_name, segments
):
    repo = tmp_path_factory.mktemp("repo")
    package_root = _make_package(repo.joinpath(*segments))
    head = _init_repo(repo, project_name)
    is_own_checkout = not segments and project_name in {
        "policyengine-us",
        "policyengine_us",
    }

    assert _get_git_sha(package_root) == (head if is_own_checkout else None)


@PROPERTY_SETTINGS
@given(segments=st.lists(PATH_SEGMENTS, max_size=4))
def test_git_sha_property_nested_checkout_reports_itself(tmp_path_factory, segments):
    outer = tmp_path_factory.mktemp("outer")
    outer_head = _init_repo(outer, "microcosm-workspace")
    package_root, head = _make_policyengine_us_checkout(
        outer.joinpath(*segments, "checkout")
    )

    assert _get_git_sha(package_root) == head != outer_head


JSON_VALUES = st.recursive(
    st.none() | st.booleans() | st.integers() | st.text(max_size=8),
    lambda children: (
        st.lists(children, max_size=3)
        | st.dictionaries(st.text(max_size=8), children, max_size=3)
    ),
    max_leaves=8,
)
COMMIT_IDS = st.one_of(
    st.text(alphabet="0123456789abcdef", min_size=40, max_size=40),
    st.text(alphabet="0123456789abcdef", min_size=64, max_size=64),
    st.text(alphabet="0123456789abcdefABCDEF", max_size=70),
    JSON_VALUES,
)
DIRECT_URLS = st.one_of(
    JSON_VALUES,
    st.fixed_dictionaries(
        {
            "url": st.text(max_size=8),
            "vcs_info": st.one_of(
                JSON_VALUES,
                st.fixed_dictionaries(
                    {
                        "vcs": st.sampled_from(["git", "hg", "svn", "bzr", "GIT"]),
                        "commit_id": COMMIT_IDS,
                    }
                ),
            ),
        }
    ),
)


@PROPERTY_SETTINGS
@given(direct_url=DIRECT_URLS)
def test_git_sha_property_installer_record_never_invents_a_sha(
    tmp_path_factory, direct_url
):
    package_root = _install_with_direct_url(
        tmp_path_factory.mktemp("site-packages"), json.dumps(direct_url)
    )
    vcs_info = direct_url.get("vcs_info") if isinstance(direct_url, dict) else None
    commit_id = vcs_info.get("commit_id") if isinstance(vcs_info, dict) else None
    is_git_commit = (
        isinstance(vcs_info, dict)
        and vcs_info.get("vcs") == "git"
        and isinstance(commit_id, str)
        and len(commit_id) in {40, 64}
        and set(commit_id) <= set("0123456789abcdef")
    )

    assert _get_direct_url_git_sha(package_root) == (
        commit_id if is_git_commit else None
    )
