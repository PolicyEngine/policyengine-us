"""Verify clean policy source and record a locally built release wheel.

The PR matrix can prepare either candidate using the actual release bump helper.
Both candidates and Publish record a receipt after the same make command.
This script never resolves dependencies or publishes.
"""

from __future__ import annotations

import hashlib
from importlib.metadata import version
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import tomllib
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]


def prepare_candidate(root: Path, kind: str) -> None:
    """Use the actual release helper, optionally preparing its rc1 counterpart."""
    if kind not in {"rc1", "final"}:
        raise ValueError("Candidate kind must be rc1 or final")
    subprocess.run(
        [sys.executable, str(root / ".github/bump_version.py")], cwd=root, check=True
    )
    if kind == "rc1":
        path = root / "pyproject.toml"
        project = path.read_text()
        final_version = tomllib.loads(project)["project"]["version"]
        prepared, count = re.subn(
            rf'^(version\s*=\s*"){re.escape(final_version)}("\s*)$',
            rf"\g<1>{final_version}rc1\g<2>",
            project,
            flags=re.MULTILINE,
        )
        if count != 1:
            raise ValueError("Expected exactly one release version assignment")
        path.write_text(prepared)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checked_build_requirements(project: dict) -> dict[str, str]:
    """Require exact pins for every declared isolated-build requirement."""
    if project["build-system"]["build-backend"] != "hatchling.build":
        raise ValueError("Release backend must match the reviewed Hatchling build")
    requirements = {}
    for requirement in project["build-system"]["requires"]:
        match = re.fullmatch(r"([A-Za-z0-9_.-]+)==([0-9][A-Za-z0-9_.]*)", requirement)
        if match is None or match[1] in requirements:
            raise ValueError("Release build requirements must be unique exact pins")
        requirements[match[1]] = match[2]
    if "hatchling" not in requirements:
        raise ValueError("Release build requires an exact Hatchling pin")
    return requirements


def wheel_identity(
    path: Path, *, expected_version: str, hatchling_version: str
) -> dict:
    """Bind wheel bytes to the requested release and its declared backend."""
    with ZipFile(path) as wheel:
        bad_member = wheel.testzip()
        if bad_member is not None:
            raise ValueError(f"Invalid wheel member: {bad_member}")
        infos = [name for name in wheel.namelist() if name.endswith(".dist-info/WHEEL")]
        if len(infos) != 1:
            raise ValueError("Expected exactly one wheel metadata directory")
        prefix = infos[0].removesuffix("WHEEL")
        metadata = wheel.read(prefix + "METADATA").decode()
        wheel_metadata = wheel.read(infos[0]).decode()
        if re.findall(r"^Version: (.+)$", metadata, re.MULTILINE) != [expected_version]:
            raise ValueError("Wheel version differs from the prepared release")
        if re.findall(r"^Generator: (.+)$", wheel_metadata, re.MULTILINE) != [
            f"hatchling {hatchling_version}"
        ]:
            raise ValueError("Wheel generator differs from the pinned backend")
    return {
        "filename": path.name,
        "sha256": _sha256(path),
        "size_bytes": path.stat().st_size,
    }


def write_build_receipt(root: Path = ROOT) -> Path:
    """Fail if tests changed package inputs, then retain only public build facts."""
    subprocess.run(
        ["git", "diff", "--exit-code", "HEAD", "--", "policyengine_us"],
        cwd=root,
        check=True,
    )
    untracked = subprocess.check_output(
        ["git", "ls-files", "--others", "--exclude-standard", "--", "policyengine_us"],
        cwd=root,
    )
    if untracked.strip():
        raise ValueError("Untracked policy source would enter the release wheel")
    project = tomllib.loads((root / "pyproject.toml").read_text())
    lock = tomllib.loads((root / "uv.lock").read_text())
    requirements = checked_build_requirements(project)
    frontend = version("build")
    locked_frontends = [
        item["version"] for item in lock["package"] if item["name"] == "build"
    ]
    if locked_frontends != [frontend]:
        raise ValueError("Installed build frontend differs from the registry lock")
    wheels = sorted((root / "dist").glob("*.whl"))
    if len(wheels) != 1:
        raise ValueError("Expected exactly one freshly built release wheel")
    receipt = {
        "source_head": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True
        ).strip(),
        "policy_tree": subprocess.check_output(
            ["git", "rev-parse", "HEAD:policyengine_us"], cwd=root, text=True
        ).strip(),
        "policy_source_matches_head": True,
        "prepared_version": project["project"]["version"],
        "pyproject_sha256": _sha256(root / "pyproject.toml"),
        "uv_lock_sha256": _sha256(root / "uv.lock"),
        "python": platform.python_version(),
        "platform": platform.system(),
        "machine": platform.machine(),
        "runner_image": {
            "os": os.environ.get("ImageOS"),
            "version": os.environ.get("ImageVersion"),
        },
        "uv": subprocess.check_output(["uv", "--version"], text=True).strip(),
        "frontend": {"name": "build", "version": frontend},
        "isolated_build_requirements": requirements,
        "wheel": wheel_identity(
            wheels[0],
            expected_version=project["project"]["version"],
            hatchling_version=requirements["hatchling"],
        ),
    }
    output = root / "release-build" / "receipt.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return output


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", choices=("rc1", "final"))
    args = parser.parse_args()
    if args.prepare:
        prepare_candidate(ROOT, args.prepare)
    else:
        print(write_build_receipt().read_text(), end="")
