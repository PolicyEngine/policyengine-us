"""Validate a release lock, or refresh only its automatic version bump.

Dependency changes belong in a reviewed registry lock before versioning runs.
This helper uses only the standard library and never imports the country model.
"""

from __future__ import annotations

import argparse
import copy
import os
from pathlib import Path
import re
import subprocess
import sys
import tomllib
from urllib.parse import unquote, urlsplit


REPO_ROOT = Path(__file__).resolve().parents[1]
PYPI = "https://pypi.org/simple"


def load_toml(path: Path) -> dict:
    """Read project or lock metadata without importing its package."""
    return tomllib.loads(path.read_text(encoding="utf-8"))


def normalized_name(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def validate_registry_project(project: dict) -> None:
    """Reject local, direct-URL, workspace and alternate-index requirements."""
    uv = project.get("tool", {}).get("uv", {})
    forbidden = {
        "sources",
        "index",
        "workspace",
        "find-links",
        "index-url",
        "extra-index-url",
        "default-index",
        "no-index",
    }
    if forbidden.intersection(uv):
        raise ValueError(
            "Release project must use PyPI without source/index/workspace overrides"
        )

    def validate_requirements(value):
        if isinstance(value, str):
            # Registry requirements may have version constraints, extras and
            # environment markers, but never a URL or filesystem path.
            requirement = value.split(";", 1)[0].strip()
            if not re.match(r"^[A-Za-z0-9][A-Za-z0-9._-]*", requirement) or any(
                char in requirement for char in "@/:\\"
            ):
                raise ValueError(
                    "Release requirements must use the registry, not URLs or paths"
                )
        elif isinstance(value, list):
            for item in value:
                validate_requirements(item)
        elif isinstance(value, dict):
            for item in value.values():
                validate_requirements(item)
        else:
            raise ValueError("Invalid release requirement metadata")

    metadata = project["project"]
    for requirements in (
        metadata.get("dependencies", []),
        metadata.get("optional-dependencies", {}),
        project.get("dependency-groups", {}),
        project.get("build-system", {}).get("requires", []),
        uv.get("constraint-dependencies", []),
        uv.get("override-dependencies", []),
        uv.get("build-constraint-dependencies", []),
    ):
        validate_requirements(requirements)


def validate_artifact(artifact: dict, package_name: str) -> None:
    """Require a hashed PyPI-hosted artifact, even under a PyPI source label."""
    if not isinstance(artifact, dict) or set(artifact) - {
        "url",
        "hash",
        "size",
        "upload-time",
    }:
        raise ValueError(f"Invalid registry artifact fields for {package_name}")
    url = artifact.get("url")
    digest = artifact.get("hash")
    if not isinstance(url, str) or any(
        char.isspace() or ord(char) < 32 for char in url
    ):
        raise ValueError(f"Missing or invalid registry artifact URL for {package_name}")
    parsed = urlsplit(url)
    path = unquote(parsed.path)
    if (
        parsed.scheme != "https"
        or parsed.netloc != "files.pythonhosted.org"
        or parsed.query
        or parsed.fragment
        or "?" in url
        or "#" in url
        or not path.startswith("/packages/")
        or "\\" in path
        or "%" in path
        or any(part in {"", ".", ".."} for part in path.split("/")[1:])
        or path != parsed.path
    ):
        raise ValueError(
            f"Artifact for {package_name} must have a canonical PyPI files URL"
        )
    if not isinstance(digest, str) or not re.fullmatch(
        r"sha256:[0-9a-fA-F]{64}", digest
    ):
        raise ValueError(f"Artifact for {package_name} must have a SHA-256 hash")


def validate_lock_requirements(value) -> None:
    """Reject alternate transports in lock dependency edges and metadata too."""
    if isinstance(value, dict):
        if {"url", "git", "path", "directory", "editable", "virtual"}.intersection(
            value
        ):
            raise ValueError("Release lock requirement contains a non-registry source")
        if "registry" in value and value["registry"] != PYPI:
            raise ValueError("Release lock requirement must use the PyPI registry")
        for item in value.values():
            validate_lock_requirements(item)
    elif isinstance(value, list):
        for item in value:
            validate_lock_requirements(item)


def validate_registry_lock(
    project: dict, lock: dict, *, allow_previous_version: bool = False
) -> None:
    """The editable root is the only package allowed outside ordinary PyPI."""
    metadata = project["project"]
    root_name = normalized_name(metadata["name"])
    roots = []
    for package in lock.get("package", []):
        name = package["name"]
        if normalized_name(name) == root_name:
            roots.append(package)
            if package.get("source") != {"editable": "."}:
                raise ValueError(
                    "Release lock root must be the current editable checkout"
                )
            if "sdist" in package or "wheels" in package:
                raise ValueError(
                    "Editable release root must not contain registry artifacts"
                )
        else:
            if package.get("source") != {"registry": PYPI}:
                raise ValueError(
                    f"Release lock dependency {name} must use the PyPI registry"
                )
            artifacts = []
            if "sdist" in package:
                artifacts.append(package["sdist"])
            wheels = package.get("wheels", [])
            if not isinstance(wheels, list):
                raise ValueError(f"Invalid registry wheel list for {name}")
            artifacts.extend(wheels)
            if not artifacts:
                raise ValueError(
                    f"Release lock dependency {name} has no registry artifacts"
                )
            for artifact in artifacts:
                validate_artifact(artifact, name)
        for key in (
            "dependencies",
            "optional-dependencies",
            "dev-dependencies",
            "metadata",
        ):
            validate_lock_requirements(package.get(key, {}))
    if len(roots) != 1:
        raise ValueError("Release lock must contain exactly one root package")
    if not allow_previous_version and roots[0].get("version") != metadata["version"]:
        raise ValueError("Release lock root version differs from pyproject.toml")
    # uv normalizes spacing in specifier lists; --check validates their meaning.
    if re.sub(r"\s", "", lock.get("requires-python", "")) != re.sub(
        r"\s", "", metadata["requires-python"]
    ):
        raise ValueError("Release lock Python range differs from pyproject.toml")


def without_root_version(lock: dict, root_name: str) -> dict:
    """Retain the entire reviewed lock graph except the editable root version."""
    result = copy.deepcopy(lock)
    for package in result["package"]:
        if normalized_name(package["name"]) == normalized_name(root_name):
            package.pop("version", None)
    return result


def resolver_environment() -> dict[str, str]:
    """Discard inherited resolver overrides and active project environments."""
    env = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith(("UV_", "PIP_"))
        and key not in {"VIRTUAL_ENV", "CONDA_PREFIX", "PYTHONPATH", "PYTHONHOME"}
    }
    env["UV_FROZEN"] = "0"
    return env


def require_committed_files(root: Path) -> None:
    """A locally repaired lock or project must not stand in for reviewed HEAD."""
    for name in ("pyproject.toml", "uv.lock"):
        path = root / name
        result = subprocess.run(
            ["git", "show", f"HEAD:{name}"], cwd=root, check=True, capture_output=True
        )
        if path.is_symlink() or path.read_bytes() != result.stdout:
            raise ValueError(
                f"Release check requires committed {name}; working bytes differ from HEAD"
            )


def reject_parent_workspaces(root: Path) -> None:
    """Prevent uv from checking or rewriting an ancestor's workspace lock."""
    # --no-config and --no-sources do not disable workspace discovery. Refuse
    # workspace ancestors even when they claim to exclude this checkout.
    for parent in root.resolve().parents:
        project_path = parent / "pyproject.toml"
        if project_path.is_file() and "workspace" in load_toml(project_path).get(
            "tool", {}
        ).get("uv", {}):
            raise ValueError("Release checkout must not be inside a uv workspace")


def check_release_lock(
    root: Path = REPO_ROOT, *, refresh: bool = False, committed: bool = False
) -> None:
    """Check with uv, or transactionally refresh only the bumped root version."""
    if refresh and committed:
        raise ValueError("Use committed checks before the bump and refresh after it")
    reject_parent_workspaces(root)
    if committed:
        require_committed_files(root)
    project = load_toml(root / "pyproject.toml")
    validate_registry_project(project)
    lock_path = root / "uv.lock"
    if lock_path.is_symlink():
        raise ValueError("Release lock must be a regular checkout file")
    before_bytes = lock_path.read_bytes()
    before = tomllib.loads(before_bytes.decode("utf-8"))
    validate_registry_lock(project, before, allow_previous_version=refresh)
    command = [
        "uv",
        "lock",
        "--no-config",
        "--no-sources",
        "--default-index",
        PYPI,
        "--python",
        sys.executable,
        "--no-python-downloads",
        "--no-cache",
    ]
    kwargs = {"cwd": root, "env": resolver_environment(), "check": True}
    successful = False
    try:
        if refresh:
            subprocess.run(command, **kwargs)
            after = load_toml(lock_path)
            validate_registry_lock(project, after)
            name = project["project"]["name"]
            if without_root_version(before, name) != without_root_version(after, name):
                raise ValueError(
                    "Versioning changed the reviewed dependency graph; prepare and review a registry lock first"
                )
        checked_bytes = lock_path.read_bytes()
        subprocess.run([*command, "--check"], **kwargs)
        if lock_path.read_bytes() != checked_bytes:
            raise ValueError("uv lock --check unexpectedly changed the release lock")
        successful = True
    finally:
        # Includes resolver errors, invalid TOML, drift, failed final checks and
        # interruptions. A partial or deleted resolver output is never retained.
        if not successful:
            lock_path.write_bytes(before_bytes)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--committed",
        action="store_true",
        help="Require lock and project bytes from HEAD",
    )
    mode.add_argument(
        "--refresh",
        action="store_true",
        help="Refresh only the root version after the automatic bump",
    )
    args = parser.parse_args()
    try:
        check_release_lock(refresh=args.refresh, committed=args.committed)
    except (ValueError, OSError, KeyError, subprocess.CalledProcessError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
