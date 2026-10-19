"""Vendor the shared source-conflict register at a pinned rulespec-us commit.

PolicyEngine-US and Axiom keep one register of places where a statute
conflicts with a regulation, form, instructions, manual or agency practice:
``known-source-conflicts.yaml`` in TheAxiomFoundation/rulespec-us. This
script copies it, byte for byte, from one commit into
``policyengine_us/tests/code_health/source_conflicts/`` and records that
commit and the file's sha256 in ``pin.yaml``. The code-health test
``test_source_conflicts.py`` reads only the vendored copy, so CI never
depends on a moving branch.

    python scripts/update_source_conflicts.py --commit <40-hex rulespec-us commit>
    python scripts/update_source_conflicts.py --check   # pin matches upstream?

Bump the pin the way other pins are bumped: to a rulespec-us commit that
holds the entries your markers cite (normally a merge commit on main).
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
import urllib.request
from pathlib import Path

import yaml

REPO = "TheAxiomFoundation/rulespec-us"
REGISTER = "known-source-conflicts.yaml"
FOLDER = (
    Path(__file__).resolve().parent.parent
    / "policyengine_us"
    / "tests"
    / "code_health"
    / "source_conflicts"
)
VENDORED = FOLDER / REGISTER
PIN = FOLDER / "pin.yaml"
COMMIT_RE = re.compile(r"[0-9a-f]{40}")


def fetch(commit: str) -> bytes:
    url = f"https://raw.githubusercontent.com/{REPO}/{commit}/{REGISTER}"
    with urllib.request.urlopen(url, timeout=60) as response:
        return response.read()


def write_pin(commit: str, data: bytes) -> None:
    PIN.write_text(
        "# The rulespec-us commit known-source-conflicts.yaml is vendored from.\n"
        "# Written by scripts/update_source_conflicts.py; do not edit by hand.\n"
        + yaml.safe_dump(
            {
                "repo": REPO,
                "commit": commit,
                "path": REGISTER,
                "sha256": hashlib.sha256(data).hexdigest(),
            },
            sort_keys=False,
        )
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--commit", help="full rulespec-us commit SHA to vendor")
    group.add_argument(
        "--check",
        action="store_true",
        help="compare the vendored copy with its pinned commit",
    )
    args = parser.parse_args(argv)
    if args.check:
        pin = yaml.safe_load(PIN.read_text())
        upstream = fetch(pin["commit"])
        local = VENDORED.read_bytes()
        if upstream != local or hashlib.sha256(upstream).hexdigest() != pin["sha256"]:
            print(
                f"{VENDORED} differs from {REPO}@{pin['commit']}:{REGISTER}",
                file=sys.stderr,
            )
            return 1
        print(f"{VENDORED.name} matches {REPO}@{pin['commit'][:12]}.")
        return 0
    if not COMMIT_RE.fullmatch(args.commit):
        parser.error("--commit must be a full lowercase 40-character SHA")
    data = fetch(args.commit)
    VENDORED.write_bytes(data)
    write_pin(args.commit, data)
    print(f"Vendored {REGISTER} from {REPO}@{args.commit[:12]} ({len(data)} bytes).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
