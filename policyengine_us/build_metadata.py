from __future__ import annotations

from functools import lru_cache
import hashlib
from importlib import metadata
from pathlib import Path
import subprocess

PACKAGE_NAME = "policyengine-us"
PACKAGE_ROOT = Path(__file__).resolve().parent
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


def _get_package_version() -> str | None:
    try:
        return metadata.version(PACKAGE_NAME)
    except metadata.PackageNotFoundError:
        return None


def _get_git_sha() -> str | None:
    for candidate in (PACKAGE_ROOT, *PACKAGE_ROOT.parents):
        if not (candidate / ".git").exists():
            continue
        try:
            return subprocess.check_output(
                ["git", "-C", str(candidate), "rev-parse", "HEAD"],
                stderr=subprocess.DEVNULL,
                text=True,
            ).strip()
        except Exception:
            return None
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


def get_data_build_metadata() -> dict[str, str | None]:
    return {
        "name": PACKAGE_NAME,
        "version": _get_package_version(),
        "git_sha": _get_git_sha(),
        "data_build_fingerprint": get_data_build_fingerprint(),
    }
