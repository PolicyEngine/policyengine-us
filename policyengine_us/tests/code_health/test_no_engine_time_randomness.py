"""The model draws nothing while a simulation is built or run.

A formula is a pure, deterministic function of its inputs
(policyengine-core#500), and seeding does not exempt a draw. Stochastic
inputs such as take-up flags and the months a reported annual amount falls
in are drawn when the dataset is built and stored as input variables; the
model compares them with its rules. policyengine-core#519 checks formulas
for numpy and stdlib randomness when variables register, but a hand-written
integer hash of entity ids passes that check, so this scan looks for the
hash as well.

Checked, in every module of the package except tests (the model's formulas,
reforms, data loading, uprating and tools):
- the stdlib ``random`` and ``secrets`` modules, ``numpy.random`` and numpy
  generator classes such as ``default_rng`` and ``RandomState``;
- the builtin ``hash()``, which Python salts per process;
- hashing and checksum libraries (``hashlib``, ``zlib``, ``uuid``, ...);
- integer constants of common 64-bit and 32-bit hash mixers (splitmix64,
  murmur3, FNV, xxHash, PCG), which catch a copied hash;
- the xorshift step ``x ^ (x >> k)`` that such mixers are built from;
- calls of ``sample``, ``shuffle``, ``permutation``, ``choice`` and similar;
- ``... % n`` where the left side reads an id (a name or string ending
  ``_id``).

EXEMPT lists reviewed uses that are not draws, each for one kind in one
file. RATCHET lists today's engine-time draws that still have to move into
the data. Both fail when an entry stops matching, so entries are removed as
sites go, and RATCHET_CEILING only ever falls: RATCHET must reach zero.

The check reads syntax trees without importing the model.
"""

import ast
from pathlib import Path

import pytest


PACKAGE = Path(__file__).resolve().parents[2]
TESTS = PACKAGE / "tests"

RATCHET = {
    (
        "variables/gov/usda/snap/eligibility/work_requirements/"
        "is_receiving_unemployment_compensation.py"
    ): {
        "kinds": {"hash constant", "xorshift"},
        "reason": (
            "Transitional splitmix64 start month for datasets that do not yet "
            "store unemployment_compensation_start_month. It goes when the "
            "default dataset stores the column."
        ),
    },
}
# Lower this when a RATCHET entry goes. Never raise it.
RATCHET_CEILING = 1

EXEMPT = {
    ("system.py", "hash library"): (
        "SHA-256 content check of the default dataset file, not a draw"
    ),
    ("build_metadata.py", "hash library"): (
        "SHA-256 fingerprint of the build for provenance, not a draw"
    ),
    ("tools/taxsim/generate_taxsim_tests.py", "sampling call"): (
        "Offline generator of YAML tests from TAXSIM output; the model never "
        "imports it (checked below)"
    ),
}
# Modules exempt because the model never runs them; nothing else may import
# them.
OFFLINE_MODULES = {"policyengine_us.tools.taxsim"}

RANDOM_MODULES = {"random", "secrets"}
HASH_MODULES = {
    "hashlib",
    "zlib",
    "binascii",
    "uuid",
    "mmh3",
    "xxhash",
    "blake3",
    "crcmod",
}
GENERATOR_NAMES = {
    "default_rng",
    "RandomState",
    "SeedSequence",
    "BitGenerator",
    "PCG64",
    "PCG64DXSM",
    "MT19937",
    "Philox",
    "SFC64",
}
SAMPLING_METHODS = {
    "sample",
    "shuffle",
    "permutation",
    "permuted",
    "choice",
    "choices",
    "randint",
    "randrange",
}
HASH_CONSTANTS = {
    # splitmix64: golden gamma and the two finalizer multipliers
    0x9E3779B97F4A7C15,
    0xBF58476D1CE4E5B9,
    0x94D049BB133111EB,
    # murmur3 fmix64 and fmix32
    0xFF51AFD7ED558CCD,
    0xC4CEB9FE1A85EC53,
    0x85EBCA6B,
    0xC2B2AE35,
    # FNV-1a 64-bit and 32-bit offset bases and primes
    0xCBF29CE484222325,
    0x100000001B3,
    0x811C9DC5,
    0x01000193,
    # xxHash64 primes
    0x9E3779B185EBCA87,
    0xC2B2AE3D27D4EB4F,
    0x165667B19E3779F9,
    0x85EBCA77C2B2AE63,
    0x27D4EB2F165667C5,
    # PCG and Knuth MMIX 64-bit LCG multiplier
    0x5851F42D4C957F2D,
}


def _reads_an_id(node) -> bool:
    for child in ast.walk(node):
        if isinstance(child, ast.Name) and child.id.endswith("_id"):
            return True
        if (
            isinstance(child, ast.Constant)
            and isinstance(child.value, str)
            and child.value.endswith("_id")
        ):
            return True
    return False


def _is_xorshift(node: ast.BinOp) -> bool:
    """``x ^ (x >> k)`` or ``x ^ (x << k)``, in either order."""
    for shifted, other in ((node.left, node.right), (node.right, node.left)):
        if (
            isinstance(shifted, ast.BinOp)
            and isinstance(shifted.op, (ast.RShift, ast.LShift))
            and ast.dump(shifted.left) == ast.dump(other)
        ):
            return True
    return False


def draw_findings(source: str, filename: str = "<string>") -> list[tuple]:
    """(line, kind) for every draw pattern in ``source``."""
    tree = ast.parse(source, filename=filename)
    findings = set()
    for node in ast.walk(tree):
        line = getattr(node, "lineno", 0)
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if alias.name == "numpy.random":
                    findings.add((line, "numpy.random"))
                elif root in RANDOM_MODULES:
                    findings.add((line, "random module"))
                elif root in HASH_MODULES:
                    findings.add((line, "hash library"))
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            root = module.split(".")[0]
            names = {alias.name for alias in node.names}
            if module == "numpy.random" or (module == "numpy" and "random" in names):
                findings.add((line, "numpy.random"))
            elif root in RANDOM_MODULES:
                findings.add((line, "random module"))
            elif root in HASH_MODULES:
                findings.add((line, "hash library"))
            if names & GENERATOR_NAMES:
                findings.add((line, "generator"))
        elif isinstance(node, ast.Attribute):
            if (
                node.attr == "random"
                and isinstance(node.value, ast.Name)
                and node.value.id in ("np", "numpy")
            ):
                findings.add((line, "numpy.random"))
            if node.attr in GENERATOR_NAMES:
                findings.add((line, "generator"))
        elif isinstance(node, ast.Name):
            if node.id in GENERATOR_NAMES:
                findings.add((line, "generator"))
        elif isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id == "hash":
                findings.add((line, "builtin hash"))
            if isinstance(func, ast.Attribute) and func.attr in SAMPLING_METHODS:
                findings.add((line, "sampling call"))
        elif isinstance(node, ast.Constant):
            value = node.value
            if (
                isinstance(value, int)
                and not isinstance(value, bool)
                and value in HASH_CONSTANTS
            ):
                findings.add((line, "hash constant"))
        elif isinstance(node, ast.BinOp):
            if isinstance(node.op, ast.BitXor) and _is_xorshift(node):
                findings.add((line, "xorshift"))
            if isinstance(node.op, ast.Mod) and _reads_an_id(node.left):
                findings.add((line, "id modulo"))
    return sorted(findings)


def package_modules():
    for path in sorted(PACKAGE.rglob("*.py")):
        if TESTS in path.parents:
            continue
        yield path.relative_to(PACKAGE).as_posix(), path


def package_findings() -> dict:
    """{(file, kind): [lines]} over the package."""
    found = {}
    for relative, path in package_modules():
        source = path.read_text(encoding="utf-8")
        for line, kind in draw_findings(source, filename=relative):
            found.setdefault((relative, kind), []).append(line)
    return found


def _allowed(relative: str, kind: str) -> bool:
    if (relative, kind) in EXEMPT:
        return True
    entry = RATCHET.get(relative)
    return entry is not None and kind in entry["kinds"]


@pytest.mark.parametrize(
    "source, kind",
    [
        ("import random\n", "random module"),
        ("from random import Random\n", "random module"),
        ("import secrets\n", "random module"),
        ("import numpy.random\n", "numpy.random"),
        ("from numpy.random import default_rng\n", "numpy.random"),
        ("from numpy.random import default_rng\n", "generator"),
        ("from numpy import random\n", "numpy.random"),
        ("x = np.random.random(3)\n", "numpy.random"),
        ("x = numpy.random.default_rng(0)\n", "numpy.random"),
        ("rng = default_rng(0)\n", "generator"),
        ("state = np.RandomState(0)\n", "generator"),
        ("key = hash(person_id)\n", "builtin hash"),
        ("import hashlib\n", "hash library"),
        ("from zlib import crc32\n", "hash library"),
        ("import uuid\n", "hash library"),
        ("m = np.uint64(0x94D049BB133111EB)\n", "hash constant"),
        ("gamma = 11400714819323198485\n", "hash constant"),
        ("h = 0xCBF29CE484222325\n", "hash constant"),
        ("x = x ^ (x >> 30)\n", "xorshift"),
        ("x = (x << 13) ^ x\n", "xorshift"),
        ("df = df.sample(frac=1)\n", "sampling call"),
        ("rng.shuffle(values)\n", "sampling call"),
        ("pick = rng.choice(5)\n", "sampling call"),
        ("month = person_id % 12\n", "id modulo"),
        ('half = person("person_id", period) % 2\n', "id modulo"),
    ],
)
def test_detector_flags_each_draw_pattern(source, kind):
    assert kind in {found_kind for _, found_kind in draw_findings(source)}


def test_detector_skips_deterministic_code():
    source = (
        "from typing import Generator\n"
        "import numpy as np\n"
        "random_state = 0\n"
        "months = np.ceil(weeks * 12 / 52)\n"
        "position = (month - 1 - start) % 12\n"
        "flags = x ^ y\n"
        "bits = x >> 3\n"
        "rank = person.get_rank(person.household, person_id)\n"
        "ok = person_id == claiming_person_id\n"
        "value = np.random_like\n"
        "big = 0xFFFFFFFFFFFFFFFF\n"
        "label = 'np.random is banned'\n"
    )
    assert draw_findings(source) == []


def test_package_draws_nothing_outside_the_allowlists():
    violations = [
        f"{relative}:{','.join(map(str, lines))}: {kind}"
        for (relative, kind), lines in sorted(package_findings().items())
        if not _allowed(relative, kind)
    ]
    assert not violations, (
        "The model must not draw, sample, shuffle or hash entities to a "
        "pseudo-random value while a simulation is built or run "
        "(policyengine-core#500). Draw in the dataset build and store the "
        "draw as an input variable; the formula then compares it with the "
        "rule, so a rate stays reformable. Draw patterns found:\n"
        + "\n".join(violations)
    )


def test_allowlist_entries_still_match():
    found = package_findings()
    stale = [
        f"EXEMPT {relative}: {kind}"
        for relative, kind in sorted(EXEMPT)
        if (relative, kind) not in found
    ]
    for relative, entry in sorted(RATCHET.items()):
        for kind in sorted(entry["kinds"]):
            if (relative, kind) not in found:
                stale.append(f"RATCHET {relative}: {kind}")
    assert not stale, (
        "These entries no longer match a draw pattern. Delete them (and "
        "lower RATCHET_CEILING for a RATCHET file that is gone):\n" + "\n".join(stale)
    )


def test_ratchet_only_shrinks():
    assert len(RATCHET) <= RATCHET_CEILING, (
        "RATCHET lists engine-time draws still to move into the data. Draw "
        "a new stochastic input in the dataset build instead of adding it."
    )


def _imported_names(node, package: str) -> list[str]:
    """Absolute module names an import statement can load."""
    if isinstance(node, ast.Import):
        return [alias.name for alias in node.names]
    if not isinstance(node, ast.ImportFrom):
        return []
    base = node.module or ""
    if node.level:
        parts = package.split(".")
        parent = ".".join(parts[: len(parts) - node.level + 1])
        base = f"{parent}.{base}" if base else parent
    return [base] + [f"{base}.{alias.name}" for alias in node.names]


def test_model_never_imports_offline_modules():
    importers = []
    for relative, path in package_modules():
        dotted = relative.removesuffix(".py").replace("/", ".")
        module = "policyengine_us." + dotted
        is_package = dotted.endswith("__init__")
        module = module.removesuffix(".__init__")
        package = module if is_package else module.rsplit(".", 1)[0]
        if any(
            module == offline or module.startswith(offline + ".")
            for offline in OFFLINE_MODULES
        ):
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=relative)
        for node in ast.walk(tree):
            names = _imported_names(node, package)
            if not names:
                continue
            for name in names:
                if any(
                    name == offline or name.startswith(offline + ".")
                    for offline in OFFLINE_MODULES
                ):
                    importers.append(f"{relative}:{node.lineno}")
    assert not importers, (
        "Offline modules are exempt from the draw check only because the "
        "model never imports them:\n" + "\n".join(importers)
    )
