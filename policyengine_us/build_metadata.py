from __future__ import annotations

from functools import lru_cache
import hashlib
from importlib import metadata
import json
import os
from pathlib import Path
import re
import subprocess
import tomllib

from policyengine_core import get_runtime_metadata as get_core_runtime_metadata

PACKAGE_NAME = "policyengine-us"
PACKAGE_ROOT = Path(__file__).resolve().parent
# Variables that point git at a repository other than the one it discovers
# from its working directory (the list `git rev-parse --local-env-vars`
# prints). They are cleared so a caller's environment, such as a git hook,
# cannot substitute another repository's HEAD.
GIT_REPOSITORY_ENV_VARS = frozenset(
    {
        "GIT_ALTERNATE_OBJECT_DIRECTORIES",
        "GIT_COMMON_DIR",
        "GIT_CONFIG",
        "GIT_CONFIG_COUNT",
        "GIT_CONFIG_PARAMETERS",
        "GIT_DIR",
        "GIT_GRAFT_FILE",
        "GIT_IMPLICIT_WORK_TREE",
        "GIT_INDEX_FILE",
        "GIT_NO_REPLACE_OBJECTS",
        "GIT_OBJECT_DIRECTORY",
        "GIT_PREFIX",
        "GIT_REPLACE_REF_BASE",
        "GIT_SHALLOW_FILE",
        "GIT_WORK_TREE",
    }
)
GIT_SHA_PATTERN = re.compile(r"[0-9a-f]{40}|[0-9a-f]{64}")
DATA_BUILD_SURFACE = (
    "entities.py",
    "parameters",
    "programs.yaml",
    "system.py",
    "variables",
)


def _iter_surface_files() -> list[Path]:
    files: list[Path] = []
    for relative_path in DATA_BUILD_SURFACE:
        path = PACKAGE_ROOT / relative_path
        if path.is_file():
            files.append(path)
            continue
        if path.is_dir():
            files.extend(
                child
                for child in sorted(path.rglob("*"))
                if child.is_file()
                and "__pycache__" not in child.parts
                and child.suffix not in {".pyc", ".pyo"}
            )
    return files


def _get_package_version() -> str:
    return metadata.version(PACKAGE_NAME)


def _get_git_sha(package_root: Path = PACKAGE_ROOT) -> str | None:
    """Return the policyengine-us commit that ``package_root`` was loaded from.

    The commit comes from one of two places:

    1. ``HEAD`` of policyengine-us's own git checkout, when the package is
       imported from one (an editable or development install, including a
       git worktree).
    2. The ``vcs_info.commit_id`` that the installer recorded in PEP 610
       ``direct_url.json`` when it installed this copy from git.

    Anything else returns None, including wheel and sdist installs. A git
    repository that merely contains the install, such as a data repository
    whose ``.venv`` holds policyengine-us, is never consulted: its HEAD is
    that repository's commit, not this package's.

    policyengine.py reads this metadata while loading the model, and
    provenance lookup must never stop that, so any failure means "unknown".
    """
    try:
        return _get_checkout_git_sha(package_root) or _get_direct_url_git_sha(
            package_root
        )
    except Exception:
        return None


def _get_checkout_git_sha(package_root: Path) -> str | None:
    # In a policyengine-us checkout the package directory sits at the
    # repository root, so the parent is the only directory to check.
    checkout_root = package_root.parent
    if not (checkout_root / ".git").exists():
        return None
    if not _declares_package(checkout_root / "pyproject.toml"):
        return None
    # Git skips an unusable .git directory and keeps searching upwards, so
    # confirm the repository it found is rooted here.
    toplevel = _run_git(checkout_root, "rev-parse", "--show-toplevel")
    if toplevel is None or not _is_same_path(Path(toplevel), checkout_root):
        return None
    return _as_git_sha(_run_git(checkout_root, "rev-parse", "HEAD"))


def _get_direct_url_git_sha(package_root: Path) -> str | None:
    # The installer writes direct_url.json into the dist-info directory next
    # to the package it installed; another copy elsewhere on sys.path does
    # not describe this one.
    try:
        distributions = list(
            metadata.distributions(
                name=PACKAGE_NAME,
                path=[str(package_root.parent)],
            )
        )
        if len(distributions) != 1:
            return None
        direct_url = json.loads(distributions[0].read_text("direct_url.json") or "{}")
    except Exception:
        return None
    vcs_info = direct_url.get("vcs_info") if isinstance(direct_url, dict) else None
    if not isinstance(vcs_info, dict) or vcs_info.get("vcs") != "git":
        return None
    return _as_git_sha(vcs_info.get("commit_id"))


def _declares_package(pyproject_path: Path) -> bool:
    try:
        with pyproject_path.open("rb") as file:
            project = tomllib.load(file).get("project")
    # tomllib raises UnicodeDecodeError (a ValueError, like TOMLDecodeError)
    # for bytes that are not UTF-8 and RecursionError for very deep nesting.
    except (OSError, ValueError, RecursionError):
        return False
    name = project.get("name") if isinstance(project, dict) else None
    return (
        isinstance(name, str) and re.sub(r"[-_.]+", "-", name).lower() == PACKAGE_NAME
    )


def _run_git(cwd: Path, *args: str) -> str | None:
    env = {
        key: value
        for key, value in os.environ.items()
        if key not in GIT_REPOSITORY_ENV_VARS
    }
    try:
        return subprocess.check_output(
            ["git", "-C", str(cwd), *args],
            stderr=subprocess.DEVNULL,
            text=True,
            env=env,
        ).strip()
    except (OSError, ValueError, subprocess.SubprocessError):
        return None


def _is_same_path(first: Path, second: Path) -> bool:
    try:
        return os.path.samefile(first, second)
    except OSError:
        return False


def _as_git_sha(value: object) -> str | None:
    if isinstance(value, str) and GIT_SHA_PATTERN.fullmatch(value):
        return value
    return None


@lru_cache(maxsize=1)
def get_data_build_fingerprint() -> str:
    digest = hashlib.sha256()
    for file_path in _iter_surface_files():
        relative_path = file_path.relative_to(PACKAGE_ROOT).as_posix()
        digest.update(relative_path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(file_path.read_bytes())
        digest.update(b"\0")
    return f"sha256:{digest.hexdigest()}"


def get_runtime_metadata() -> dict[str, object]:
    return {
        "name": PACKAGE_NAME,
        "version": _get_package_version(),
        "git_sha": _get_git_sha(),
        "data_build_fingerprint": get_data_build_fingerprint(),
        "core": get_core_runtime_metadata(),
    }


def get_data_build_metadata() -> dict[str, object]:
    return get_runtime_metadata()
