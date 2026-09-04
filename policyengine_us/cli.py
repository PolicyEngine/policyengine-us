"""The ``policyengine-us`` console entry point.

Subcommands:
    dependency-map   trace which variables read each parameter and which
                     variables feed which (see tools/dependency_map.py)
"""

from __future__ import annotations

import sys


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__.strip())
        return 0 if argv else 2
    command, rest = argv[0], argv[1:]
    if command == "dependency-map":
        from policyengine_us.tools.dependency_map import main as run

        return run(rest)
    print(f"policyengine-us: unknown command {command!r}", file=sys.stderr)
    print(__doc__.strip(), file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
