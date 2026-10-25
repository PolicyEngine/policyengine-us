"""The model draws nothing while a simulation is built or run.

A formula is a pure, deterministic function of its inputs
(policyengine-core#500), and seeding does not exempt a draw. Stochastic
inputs such as take-up flags and the months a reported annual amount falls
in are drawn when the dataset is built and stored as input variables; the
model compares them with its rules. policyengine-core#519 checks formulas
for numpy and stdlib randomness when variables register, but a hand-written
integer hash of entity ids passes that check, so this scan looks for the
hash as well.

Every module of the package except tests is parsed (formulas, reforms,
simulation code, data loading, uprating and tools). Names are resolved
through each scope's own import bindings, so ``from numpy import random as
r`` followed by ``r.random(3)`` is caught while a local variable called
``random`` is not. Formulas reach numpy through
``from policyengine_us.model_api import *``, which a syntax tree cannot
follow, so ``np`` and ``numpy`` start out bound to numpy. Reported, as
(file, enclosing function or class, kind):
- ``stochastic import``: importing ``random``, ``secrets`` or
  ``numpy.random`` (or anything from them);
- ``random source``: a name or attribute that resolves into ``numpy.random``,
  ``random`` or ``secrets``, or to ``uuid.uuid1``, ``uuid.uuid4`` or
  ``os.urandom``;
- ``builtin hash``: calling the unshadowed ``hash()``, which Python salts
  per process;
- ``hash library``: importing a hashing or checksum library (``hashlib``,
  ``zlib``, ``uuid``, ...);
- ``hash constant``: an integer constant of a common hash mixer
  (splitmix64, murmur3, FNV, xxHash, PCG), which catches a copied hash;
- ``xorshift``: the step ``x ^ (x >> k)`` such mixers are built from;
- ``sampling call``: ``.sample(...)`` with sampling arguments, or a method
  named ``shuffle``, ``permutation``, ``choice`` and the like;
- ``id modulo``: ``... % n`` where the left side reads an id (a name or
  string ending ``_id``).

This is a ratchet over recognised patterns, not a proof that no
hand-written draw exists.

EXEMPT lists reviewed occurrences that are not draws; RATCHET lists today's
engine-time draws that still have to move into the data. Both count exact
occurrences per (file, enclosing scope, kind): an extra occurrence fails, and
so does an entry that no longer matches as many as it says, so entries are
lowered and removed as sites go. RATCHET_CEILING only ever falls, and
RATCHET must reach zero.
"""

import ast
from pathlib import Path

import pytest


PACKAGE = Path(__file__).resolve().parents[2]
TESTS = PACKAGE / "tests"

RATCHET = {
    # Transitional splitmix64 start month for datasets that do not yet store
    # unemployment_compensation_start_month. It goes when the default
    # dataset stores the column.
    (
        "variables/gov/usda/snap/eligibility/work_requirements/"
        "is_receiving_unemployment_compensation.py"
    ): {
        ("<module>", "hash constant"): 2,
        ("legacy_start_month_index", "xorshift"): 3,
    },
}
# The number of RATCHET occurrences. Lower it when one goes; never raise it.
RATCHET_CEILING = 5

EXEMPT = {
    # SHA-256 content check of the default dataset file.
    "system.py": {("<module>", "hash library"): 1},
    # SHA-256 fingerprint of the build, for provenance.
    "build_metadata.py": {("<module>", "hash library"): 1},
    # Offline generator of YAML tests from TAXSIM output; the model never
    # imports it (test_model_never_imports_offline_modules).
    "tools/taxsim/generate_taxsim_tests.py": {
        ("TaxSim35.generate_from_microsimulation", "sampling call"): 2,
    },
}
OFFLINE_MODULES = {"policyengine_us.tools.taxsim"}

STAR_IMPORT_BINDINGS = {"np": "numpy", "numpy": "numpy"}
STOCHASTIC_MODULES = ("numpy.random", "random", "secrets")
STOCHASTIC_CALLABLES = {"uuid.uuid1", "uuid.uuid4", "os.urandom"}
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
SAMPLING_METHODS = {
    "shuffle",
    "permutation",
    "permuted",
    "choice",
    "choices",
    "randint",
    "randrange",
}
SAMPLING_KEYWORDS = {"n", "frac", "random_state", "weights", "replace"}
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
SCOPE_NODES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)


def _is_stochastic(target: str | None) -> bool:
    if not target:
        return False
    if target in STOCHASTIC_CALLABLES:
        return True
    return any(
        target == module or target.startswith(module + ".")
        for module in STOCHASTIC_MODULES
    )


class _Scope:
    def __init__(self, node, qualname, parent):
        self.node = node
        self.qualname = qualname
        self.parent = parent
        # name -> [(line, imported target, or None for a local value)]
        self.bindings = {}

    def bind(self, name, line, target=None):
        self.bindings.setdefault(name, []).append((line, target))

    def resolve(self, name, line):
        """The imported target ``name`` holds at ``line``, if any."""
        scope = self
        inside_function = False
        while scope is not None:
            is_class = isinstance(scope.node, ast.ClassDef)
            if name in scope.bindings and not (is_class and inside_function):
                entries = scope.bindings[name]
                earlier = [entry for entry in entries if entry[0] <= line]
                if earlier:
                    return max(earlier, key=lambda entry: entry[0])[1]
                if scope.parent is not None and not is_class:
                    # A name bound anywhere in a function is local to it.
                    return entries[0][1]
            if isinstance(scope.node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                inside_function = True
            scope = scope.parent
        return STAR_IMPORT_BINDINGS.get(name)

    def is_bound(self, name, line):
        scope = self
        while scope is not None:
            if any(entry[0] <= line for entry in scope.bindings.get(name, [])):
                return True
            if scope.parent is not None and name in scope.bindings:
                return True
            scope = scope.parent
        return False


def _bind_target(scope, target):
    for node in ast.walk(target):
        if isinstance(node, ast.Name):
            scope.bind(node.id, node.lineno)


def _bind_arguments(scope, arguments, line):
    for argument in (
        arguments.posonlyargs
        + arguments.args
        + arguments.kwonlyargs
        + [arguments.vararg, arguments.kwarg]
    ):
        if argument is not None:
            scope.bind(argument.arg, line)


def _build_scopes(tree):
    """Bindings per scope, and the innermost scope of every node."""
    module = _Scope(tree, "<module>", None)
    scope_of = {}

    def visit(node, scope):
        scope_of[node] = scope
        if isinstance(node, SCOPE_NODES):
            if not isinstance(node, ast.Lambda):
                scope.bind(node.name, node.lineno)
                for decorator in node.decorator_list:
                    visit(decorator, scope)
            name = getattr(node, "name", "<lambda>")
            qualname = name if scope.parent is None else f"{scope.qualname}.{name}"
            inner = _Scope(node, qualname, scope)
            if isinstance(node, ast.ClassDef):
                for base in node.bases + [k.value for k in node.keywords]:
                    visit(base, scope)
            else:
                # Defaults and annotations are evaluated in the outer scope.
                outer = node.args.defaults + [
                    d for d in node.args.kw_defaults if d is not None
                ]
                if not isinstance(node, ast.Lambda):
                    outer += [node.returns] if node.returns else []
                    outer += [
                        argument.annotation
                        for argument in ast.walk(node.args)
                        if isinstance(argument, ast.arg) and argument.annotation
                    ]
                for child in outer:
                    visit(child, scope)
                _bind_arguments(inner, node.args, node.lineno)
            body = node.body if isinstance(node.body, list) else [node.body]
            for child in body:
                visit(child, inner)
            return
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.asname:
                    scope.bind(alias.asname, node.lineno, alias.name)
                else:
                    root = alias.name.split(".")[0]
                    scope.bind(root, node.lineno, root)
        elif isinstance(node, ast.ImportFrom):
            module_name = node.module or ""
            for alias in node.names:
                if alias.name != "*":
                    scope.bind(
                        alias.asname or alias.name,
                        node.lineno,
                        f"{module_name}.{alias.name}",
                    )
        elif isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
            scope.bind(node.id, node.lineno)
        elif isinstance(node, ast.ExceptHandler) and node.name:
            scope.bind(node.name, node.lineno)
        for child in ast.iter_child_nodes(node):
            visit(child, scope)

    visit(tree, module)
    return scope_of


def _dotted(node):
    """('np', ['random', 'seed']) for np.random.seed, else None."""
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        return node.id, list(reversed(parts))
    return None


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
    """(line, enclosing scope, kind) for every draw pattern in ``source``."""
    tree = ast.parse(source, filename=filename)
    scope_of = _build_scopes(tree)
    parents = {
        child: node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)
    }
    findings = []

    def scope_for(node):
        while node not in scope_of:
            node = parents[node]
        return scope_of[node]

    def report(node, kind):
        findings.append((node.lineno, scope_for(node).qualname, kind))

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if _is_stochastic(alias.name):
                    report(node, "stochastic import")
                elif alias.name.split(".")[0] in HASH_MODULES:
                    report(node, "hash library")
        elif isinstance(node, ast.ImportFrom):
            module_name = node.module or ""
            imported = [f"{module_name}.{alias.name}" for alias in node.names]
            if _is_stochastic(module_name) or any(map(_is_stochastic, imported)):
                report(node, "stochastic import")
            elif module_name.split(".")[0] in HASH_MODULES:
                report(node, "hash library")
        elif isinstance(node, (ast.Name, ast.Attribute)) and isinstance(
            node.ctx, ast.Load
        ):
            parent = parents.get(node)
            if isinstance(parent, ast.Attribute) and parent.value is node:
                continue  # Only the whole chain counts.
            dotted = _dotted(node)
            if dotted is None:
                continue
            root, attributes = dotted
            target = scope_for(node).resolve(root, node.lineno)
            if target is not None and _is_stochastic(".".join([target] + attributes)):
                report(node, "random source")
        if isinstance(node, ast.Call):
            func = node.func
            if (
                isinstance(func, ast.Name)
                and func.id == "hash"
                and not scope_for(node).is_bound("hash", node.lineno)
            ):
                report(node, "builtin hash")
            if isinstance(func, ast.Attribute):
                keywords = {keyword.arg for keyword in node.keywords}
                if func.attr in SAMPLING_METHODS or (
                    func.attr == "sample"
                    and (node.args or keywords & SAMPLING_KEYWORDS)
                ):
                    report(node, "sampling call")
        elif isinstance(node, ast.Constant):
            value = node.value
            if (
                isinstance(value, int)
                and not isinstance(value, bool)
                and value in HASH_CONSTANTS
            ):
                report(node, "hash constant")
        elif isinstance(node, ast.BinOp):
            if isinstance(node.op, ast.BitXor) and _is_xorshift(node):
                report(node, "xorshift")
            if isinstance(node.op, ast.Mod) and _reads_an_id(node.left):
                report(node, "id modulo")
    return sorted(findings)


def count_findings(findings_by_file: dict) -> dict:
    """{file: {(scope, kind): [lines]}} from {file: draw_findings(...)}."""
    counted = {}
    for relative, findings in findings_by_file.items():
        for line, scope, kind in findings:
            counted.setdefault(relative, {}).setdefault((scope, kind), []).append(line)
    return counted


def check_allowlists(counted: dict, ratchet: dict, exempt: dict):
    """(violations, stale entries) of counted findings against the lists."""
    violations, stale = [], []
    allowed = {}
    for allowlist in (ratchet, exempt):
        for relative, entries in allowlist.items():
            for key, count in entries.items():
                allowed[(relative, key)] = allowed.get((relative, key), 0) + count
    for relative, entries in sorted(counted.items()):
        for (scope, kind), lines in sorted(entries.items()):
            limit = allowed.get((relative, (scope, kind)), 0)
            if len(lines) > limit:
                violations.append(
                    f"{relative}:{','.join(map(str, lines))} in {scope}: {kind} "
                    f"({len(lines)} found, {limit} allowed)"
                )
    for (relative, (scope, kind)), limit in sorted(allowed.items()):
        found = len(counted.get(relative, {}).get((scope, kind), []))
        if found < limit:
            stale.append(
                f"{relative} in {scope}: {kind} ({limit} allowed, {found} found)"
            )
    return violations, stale


def package_modules():
    for path in sorted(PACKAGE.rglob("*.py")):
        if TESTS in path.parents:
            continue
        yield path.relative_to(PACKAGE).as_posix(), path


def package_counts() -> dict:
    return count_findings(
        {
            relative: draw_findings(path.read_text(encoding="utf-8"), relative)
            for relative, path in package_modules()
        }
    )


def _kinds(source: str) -> set:
    return {kind for _, _, kind in draw_findings(source)}


@pytest.mark.parametrize(
    "source, kind",
    [
        ("import random\n", "stochastic import"),
        ("from random import uniform\nuniform()\n", "random source"),
        ("import random as rnd\nrnd.random()\n", "random source"),
        ("import secrets\n", "stochastic import"),
        ("import numpy.random as npr\nnpr.uniform()\n", "random source"),
        ("from numpy import random as r\nr.random(3)\n", "random source"),
        ("from numpy import random as r\n", "stochastic import"),
        ("from numpy.random import default_rng as g\ng(43)\n", "random source"),
        ("np.random.seed(1)\n", "random source"),
        ("import numpy as n\nn.random.default_rng(0)\n", "random source"),
        ("def f():\n    return np.random.random(3)\n", "random source"),
        ("import uuid\nuuid.uuid4()\n", "random source"),
        ("import os\nos.urandom(8)\n", "random source"),
        ('key = hash("x")\n', "builtin hash"),
        ("import hashlib\n", "hash library"),
        ("from zlib import crc32\n", "hash library"),
        ("m = np.uint64(0x94D049BB133111EB)\n", "hash constant"),
        ("gamma = 11400714819323198485\n", "hash constant"),
        ("h = 0xCBF29CE484222325\n", "hash constant"),
        ("x = x ^ (x >> 30)\n", "xorshift"),
        ("x = (x << 13) ^ x\n", "xorshift"),
        ("df = df.sample(frac=0.5, random_state=1)\n", "sampling call"),
        ("df = df.sample(5)\n", "sampling call"),
        ("rng.shuffle(values)\n", "sampling call"),
        ("pick = rng.choice(5)\n", "sampling call"),
        ("month = person_id % 12\n", "id modulo"),
        ('half = person("person_id", period) % 2\n', "id modulo"),
    ],
)
def test_detector_flags_each_draw_pattern(source, kind):
    assert kind in _kinds(source)


@pytest.mark.parametrize(
    "source",
    [
        "from typing import Generator\ndef f(Generator):\n    return Generator\n",
        "random = 3\nrandom + 1\n",
        "def f(random):\n    return random.random()\n",
        "def hash(x):\n    return x\nhash(1)\n",
        '"""np.random.seed is banned"""\nlabel = "np.random"\n',
        "obj.random_seed\nobj.sample()\n",
        "months = np.ceil(weeks * 12 / 52)\nposition = (month - 1 - start) % 12\n",
        "flags = x ^ y\nbits = x >> 3\nbig = 0xFFFFFFFFFFFFFFFF\n",
        "rank = person.get_rank(person.household, person_id)\n",
        "import numpy as np\nnp.random_like = 1\nvalue = np.where(a, b, c)\n",
        "def f():\n    np = object()\n    return np.random\n",
    ],
)
def test_detector_skips_deterministic_code(source):
    assert draw_findings(source) == []


def test_allowlist_counts_occurrences_per_scope():
    source = (
        "def first():\n"
        "    return np.random.random()\n"
        "def second():\n"
        "    return np.random.random()\n"
    )
    counted = count_findings({"m.py": draw_findings(source)})
    one = {"m.py": {("first", "random source"): 1}}
    # An occurrence in a new function of an allowlisted file fails.
    violations, stale = check_allowlists(counted, one, {})
    assert len(violations) == 1 and "second" in violations[0] and not stale
    # A second occurrence in an allowlisted scope fails.
    twice = count_findings({"m.py": draw_findings(source.replace("second", "first"))})
    violations, _ = check_allowlists(twice, one, {})
    assert violations and "2 found, 1 allowed" in violations[0]
    # An entry that allows more than it matches is stale.
    _, stale = check_allowlists(counted, {"m.py": {("first", "random source"): 2}}, {})
    assert stale and "2 allowed, 1 found" in stale[0]


def test_package_draws_nothing_outside_the_allowlists():
    violations, _ = check_allowlists(package_counts(), RATCHET, EXEMPT)
    assert not violations, (
        "The model must not draw, sample, shuffle or hash entities to a "
        "pseudo-random value while a simulation is built or run "
        "(policyengine-core#500). Draw in the dataset build and store the "
        "draw as an input variable; the formula then compares it with the "
        "rule, so a rate stays reformable. Draw patterns found:\n"
        + "\n".join(violations)
    )


def test_allowlist_entries_still_match():
    _, stale = check_allowlists(package_counts(), RATCHET, EXEMPT)
    assert not stale, (
        "These entries allow more than the package now has. Lower or delete "
        "them, and lower RATCHET_CEILING to match RATCHET:\n" + "\n".join(stale)
    )


def test_ratchet_only_shrinks():
    total = sum(sum(entries.values()) for entries in RATCHET.values())
    assert total <= RATCHET_CEILING, (
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
        is_package = dotted.endswith("__init__")
        module = ("policyengine_us." + dotted).removesuffix(".__init__")
        package = module if is_package else module.rsplit(".", 1)[0]
        if any(
            module == offline or module.startswith(offline + ".")
            for offline in OFFLINE_MODULES
        ):
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=relative)
        for node in ast.walk(tree):
            for name in _imported_names(node, package):
                if any(
                    name == offline or name.startswith(offline + ".")
                    for offline in OFFLINE_MODULES
                ):
                    importers.append(f"{relative}:{node.lineno}")
    assert not importers, (
        "Offline modules are exempt from the draw check only because the "
        "model never imports them:\n" + "\n".join(importers)
    )
