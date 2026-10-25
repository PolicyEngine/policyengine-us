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
simulation code, data loading, uprating and tools). Names are resolved under
Python's scoping rules: imports, assignments of one name or attribute to
another (``xp = np``), default arguments, functions, lambdas, comprehensions,
and class bodies that their methods cannot see. So ``from numpy import random
as r`` followed by ``r.random(3)`` is caught, and so are ``xp = np`` followed
by ``xp.random.uniform()`` and ``from numpy import *`` followed by
``random.uniform()``, while a local variable called ``random`` is not. A star
import binds every public name the imported package module defines or
imports, or the names STAR_EXPORTS lists for numpy and
``policyengine_core.model_api``; ``np``, ``numpy`` and ``pd`` are bound to
numpy and pandas wherever nothing else binds them. Reported, as (file,
enclosing function or class, kind):
- ``stochastic import``: importing ``random``, ``secrets`` or
  ``numpy.random`` (or anything from them), including through
  ``importlib.import_module`` or ``__import__`` with a literal name;
- ``random source``: a name or attribute that resolves into ``numpy.random``,
  ``random`` or ``secrets``, or to ``uuid.uuid1``, ``uuid.uuid4`` or
  ``os.urandom``, including through ``getattr`` with a literal name;
- ``builtin hash``: any use of the unshadowed ``hash``, which Python salts
  per process;
- ``hash library``: importing a hashing or checksum library (``hashlib``,
  ``zlib``, ``uuid``, ...);
- ``hash use``: a name or attribute that resolves into one of those
  libraries or to pandas' hashing functions, so that a new use of an
  import EXEMPT allows still counts;
- ``hash constant``: an integer constant of a common hash mixer
  (splitmix64, murmur3, FNV, xxHash, PCG), which catches a copied hash;
- ``xorshift``: the step ``x ^ (x >> k)`` such mixers are built from,
  written with operators, ``^=`` or numpy's ``bitwise_xor`` and shifts;
- ``sampling call``: ``.sample(...)`` with sampling arguments, or a method
  named ``shuffle``, ``permutation``, ``choice`` and the like;
- ``id modulo``: ``... % n``, ``%=``, ``np.mod``, ``divmod`` and the like,
  where the dividend reads an id (a name or string ending ``_id``);
- ``draw helper call``: a use of a top-level function of the package whose
  body has a finding EXEMPT does not cover, or that itself uses such a
  function, so that calling an existing draw again also counts.

This is a ratchet over recognised patterns, not a proof that no
hand-written draw exists. It does not follow ``eval`` or ``exec``, imports
of a computed name, values reached through objects (``self.r = np.random``
is caught where ``np.random`` is read, a later ``self.r.uniform()`` is not),
or methods as draw helpers.

EXEMPT lists reviewed occurrences that are not draws; RATCHET lists today's
engine-time draws that still have to move into the data. Both count exact
occurrences per (file, enclosing scope, kind): an extra occurrence fails, and
so does an entry that no longer matches as many as it says, so entries are
lowered and removed as sites go. RATCHET_CEILING only ever falls, and
RATCHET must reach zero.
"""

import ast
from collections import Counter
from functools import cache
from pathlib import Path
from typing import NamedTuple

import pytest


PACKAGE = Path(__file__).resolve().parents[2]
TESTS = PACKAGE / "tests"

RATCHET = {
    # Transitional splitmix64 start month for datasets that do not yet store
    # unemployment_compensation_start_month, and the two calls that reach it.
    # They go when the national and ACS local-area releases store the column.
    (
        "variables/gov/usda/snap/eligibility/work_requirements/"
        "is_receiving_unemployment_compensation.py"
    ): {
        ("<module>", "hash constant"): 2,
        ("legacy_start_month_index", "xorshift"): 3,
        ("stored_start_month_index", "draw helper call"): 1,
        ("is_receiving_unemployment_compensation.formula", "draw helper call"): 1,
    },
}
# The number of RATCHET occurrences. Lower it when one goes; never raise it.
RATCHET_CEILING = 7

EXEMPT = {
    # SHA-256 content check of the default dataset file.
    "system.py": {
        ("<module>", "hash library"): 1,
        ("_file_sha256", "hash use"): 1,
    },
    # SHA-256 fingerprint of the build, for provenance.
    "build_metadata.py": {
        ("<module>", "hash library"): 1,
        ("get_data_build_fingerprint", "hash use"): 1,
    },
    # Offline generator of YAML tests from TAXSIM output; the model never
    # imports it (test_model_never_imports_offline_modules).
    "tools/taxsim/generate_taxsim_tests.py": {
        ("TaxSim35.generate_from_microsimulation", "sampling call"): 2,
    },
}
OFFLINE_MODULES = {"policyengine_us.tools.taxsim"}

# Names a star import of a module outside the package binds, where they
# matter here. numpy's __all__ includes its random module.
STAR_EXPORTS = {
    "numpy": {"random": "numpy.random"},
    "policyengine_core.model_api": {
        "np": "numpy",
        "numpy": "numpy",
        "pd": "pandas",
        # Core's guard that raises on formula-time randomness.
        "random": "policyengine_core.commons.formulas.random",
    },
}
# What a name bound nowhere in the module refers to.
UNBOUND_NAMES = {
    "np": "numpy",
    "numpy": "numpy",
    "pd": "pandas",
    "hash": "builtins.hash",
    "getattr": "builtins.getattr",
    "__import__": "builtins.__import__",
    "divmod": "builtins.divmod",
}
DYNAMIC_IMPORTS = {"importlib.import_module", "builtins.__import__"}
XOR_FUNCTIONS = {"numpy.bitwise_xor", "operator.xor"}
SHIFT_FUNCTIONS = {
    "numpy.right_shift",
    "numpy.left_shift",
    "operator.rshift",
    "operator.lshift",
}
MOD_FUNCTIONS = {
    "numpy.mod",
    "numpy.remainder",
    "numpy.fmod",
    "operator.mod",
    "builtins.divmod",
}
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
HASH_APIS = (
    "pandas.util.hash_pandas_object",
    "pandas.util.hash_array",
    "pandas.core.util.hashing",
)
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
FUNCTION_NODES = (ast.FunctionDef, ast.AsyncFunctionDef)
COMPREHENSION_NODES = (ast.ListComp, ast.SetComp, ast.GeneratorExp, ast.DictComp)
# Scopes whose names a class body nested in them cannot hide.
FUNCTION_LIKE_NODES = FUNCTION_NODES + (ast.Lambda,) + COMPREHENSION_NODES
# Alias chains longer than this are treated as unresolved.
MAX_ALIAS_DEPTH = 32


def _matches(target: str, prefixes) -> bool:
    return any(
        target == prefix or target.startswith(prefix + ".") for prefix in prefixes
    )


def _is_stochastic(target: str | None) -> bool:
    if not target:
        return False
    return target in STOCHASTIC_CALLABLES or _matches(target, STOCHASTIC_MODULES)


def _classify(target: str) -> str | None:
    """The kind of finding a use of ``target`` is, if any."""
    if _is_stochastic(target):
        return "random source"
    if target == "builtins.hash":
        return "builtin hash"
    if target.split(".")[0] in HASH_MODULES or _matches(target, HASH_APIS):
        return "hash use"
    return None


def _absolute(module: str, level: int, package: str | None) -> str:
    """The absolute name of a ``from`` import's module."""
    if not level:
        return module
    if package is None:
        return "." * level + module
    parts = package.split(".")
    parent = ".".join(parts[: len(parts) - level + 1])
    return f"{parent}.{module}" if module else parent


def _dotted(node):
    """('np', ['random', 'seed']) for np.random.seed, else None."""
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        return node.id, list(reversed(parts))
    return None


class _Alias:
    """A name bound, at ``line``, to another name or attribute chain."""

    def __init__(self, scope, value, line):
        self.scope = scope
        self.root, self.attributes = _dotted(value)
        self.line = line

    def target(self, depth):
        # The value is evaluated before the name is bound.
        target = self.scope.resolve(self.root, self.line, depth + 1, before=True)
        return ".".join([target] + self.attributes) if target else None


class _Scope:
    def __init__(self, node, qualname, parent):
        self.node = node
        self.qualname = qualname
        self.parent = parent
        # name -> [(line, target)]. The target is what the name refers to (a
        # module, function or other import), an _Alias, or None for a value.
        self.bindings = {}

    def bind(self, name, line, target=None):
        self.bindings.setdefault(name, []).append((line, target))

    def resolve(self, name, line, depth=0, before=False):
        """What ``name`` refers to at ``line``; None for a local value.

        ``before`` excludes bindings made on ``line`` itself.
        """
        if depth > MAX_ALIAS_DEPTH:
            return None
        scope = self
        # Whether the lookup started inside a function-like scope that
        # ``scope`` encloses: such code cannot see class bodies around it,
        # and runs after the module's top level has bound everything.
        from_function = False
        while scope is not None:
            is_class = isinstance(scope.node, ast.ClassDef)
            entries = scope.bindings.get(name)
            if entries and not (is_class and from_function):
                if scope.parent is None and from_function:
                    entry = max(entries, key=lambda entry: entry[0])
                    return self._target(entry, depth)
                earlier = [
                    entry
                    for entry in entries
                    if entry[0] < line or (entry[0] == line and not before)
                ]
                if earlier:
                    entry = max(earlier, key=lambda entry: entry[0])
                    return self._target(entry, depth)
                if scope.parent is not None and not is_class:
                    # A name bound anywhere in a function is local to it.
                    return self._target(entries[0], depth)
            if isinstance(scope.node, FUNCTION_LIKE_NODES):
                from_function = True
            scope = scope.parent
        return UNBOUND_NAMES.get(name)

    @staticmethod
    def _target(entry, depth):
        target = entry[1]
        return target.target(depth) if isinstance(target, _Alias) else target


def _alias(scope, value, line):
    """What binding ``value`` at ``line`` binds: an _Alias of a name or chain."""
    if value is not None and _dotted(value) is not None:
        return _Alias(scope, value, line)
    return None


def _build_scopes(tree, module, package, star_exports):
    """Bindings per scope, and the innermost scope of every node."""
    top = _Scope(tree, "<module>", None)
    scope_of = {}

    def assign(target, value, scope):
        scope_of[target] = scope
        if isinstance(target, ast.Name):
            scope.bind(target.id, target.lineno, _alias(scope, value, target.lineno))
        elif (
            isinstance(target, (ast.Tuple, ast.List))
            and isinstance(value, (ast.Tuple, ast.List))
            and len(target.elts) == len(value.elts)
        ):
            for element, element_value in zip(target.elts, value.elts):
                assign(element, element_value, scope)
        else:
            visit(target, scope)

    def bind_arguments(inner, outer, arguments, line):
        positional = arguments.posonlyargs + arguments.args
        defaults = [None] * (len(positional) - len(arguments.defaults))
        defaults += arguments.defaults
        pairs = list(zip(positional, defaults))
        pairs += list(zip(arguments.kwonlyargs, arguments.kw_defaults))
        pairs += [(arguments.vararg, None), (arguments.kwarg, None)]
        for argument, default in pairs:
            if argument is not None:
                inner.bind(argument.arg, line, _alias(outer, default, line))

    def visit_function(node, scope):
        # Decorators, defaults and annotations are evaluated in the outer
        # scope.
        outer = list(getattr(node, "decorator_list", []))
        outer += node.args.defaults + [d for d in node.args.kw_defaults if d]
        if not isinstance(node, ast.Lambda):
            outer += [node.returns] if node.returns else []
            outer += [
                argument.annotation
                for argument in ast.walk(node.args)
                if isinstance(argument, ast.arg) and argument.annotation
            ]
        for child in outer:
            visit(child, scope)
        name = getattr(node, "name", "<lambda>")
        if not isinstance(node, ast.Lambda):
            top_level = scope.parent is None
            scope.bind(name, node.lineno, f"{module}.{name}" if top_level else None)
        qualname = name if scope.parent is None else f"{scope.qualname}.{name}"
        inner = _Scope(node, qualname, scope)
        bind_arguments(inner, scope, node.args, node.lineno)
        for child in node.body if isinstance(node.body, list) else [node.body]:
            visit(child, inner)

    def visit_class(node, scope):
        for child in node.decorator_list + node.bases:
            visit(child, scope)
        for keyword in node.keywords:
            visit(keyword.value, scope)
        top_level = scope.parent is None
        scope.bind(
            node.name, node.lineno, f"{module}.{node.name}" if top_level else None
        )
        qualname = node.name if top_level else f"{scope.qualname}.{node.name}"
        inner = _Scope(node, qualname, scope)
        for child in node.body:
            visit(child, inner)

    def visit_comprehension(node, scope):
        # The first iterable is evaluated in the enclosing scope; the rest
        # in the comprehension's own, reported under the enclosing name.
        visit(node.generators[0].iter, scope)
        inner = _Scope(node, scope.qualname, scope)
        for index, generator in enumerate(node.generators):
            scope_of[generator] = inner
            if index:
                visit(generator.iter, inner)
            assign(generator.target, None, inner)
            for condition in generator.ifs:
                visit(condition, inner)
        if isinstance(node, ast.DictComp):
            elements = [node.key, node.value]
        else:
            elements = [node.elt]
        for element in elements:
            visit(element, inner)

    def visit(node, scope):
        scope_of[node] = scope
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            return visit_function(node, scope)
        if isinstance(node, ast.ClassDef):
            return visit_class(node, scope)
        if isinstance(node, COMPREHENSION_NODES):
            return visit_comprehension(node, scope)
        if isinstance(node, ast.Assign):
            visit(node.value, scope)
            for target in node.targets:
                assign(target, node.value, scope)
            return
        if isinstance(node, ast.AnnAssign):
            visit(node.annotation, scope)
            if node.value is not None:
                visit(node.value, scope)
            return assign(node.target, node.value, scope)
        if isinstance(node, ast.NamedExpr):
            visit(node.value, scope)
            owner = scope
            while isinstance(owner.node, COMPREHENSION_NODES):
                owner = owner.parent
            return assign(node.target, node.value, owner)
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.asname:
                    scope.bind(alias.asname, node.lineno, alias.name)
                else:
                    root = alias.name.split(".")[0]
                    scope.bind(root, node.lineno, root)
        elif isinstance(node, ast.ImportFrom):
            base = _absolute(node.module or "", node.level, package)
            for alias in node.names:
                if alias.name == "*":
                    for name, target in star_exports(base).items():
                        scope.bind(name, node.lineno, target)
                else:
                    scope.bind(
                        alias.asname or alias.name,
                        node.lineno,
                        f"{base}.{alias.name}",
                    )
        elif isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
            scope.bind(node.id, node.lineno)
        elif isinstance(node, ast.ExceptHandler) and node.name:
            scope.bind(node.name, node.lineno)
        for child in ast.iter_child_nodes(node):
            visit(child, scope)

    visit(tree, top)
    return scope_of


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


def _is_xorshift(left, right, shift_of) -> bool:
    """``x ^ (x >> k)`` or ``x ^ (x << k)``, in either order.

    ``shift_of`` gives the shifted operand of a shift, or None.
    """
    for shifted, other in ((left, right), (right, left)):
        operand = shift_of(shifted)
        if operand is not None and ast.unparse(operand) == ast.unparse(other):
            return True
    return False


def _literal(node) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


class Analysis(NamedTuple):
    module: str
    # (line, enclosing scope, kind), without draw helper calls.
    findings: list
    # (line, enclosing scope, target) for each use of a package name.
    references: list
    # Names of the module's top-level functions.
    functions: list
    # (line, absolute module name) for each import, static or literal dynamic.
    imports: list


def _no_star_exports(module):
    return STAR_EXPORTS.get(module, {})


def analyse(
    source: str,
    filename: str = "<string>",
    module: str = "m",
    package: str | None = None,
    star_exports=_no_star_exports,
) -> Analysis:
    """Draw patterns, package references and imports of one module."""
    tree = ast.parse(source, filename=filename)
    scope_of = _build_scopes(tree, module, package, star_exports)
    parents = {
        child: node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)
    }
    root_package = module.split(".")[0] + "."
    findings, references, imports = [], [], []

    def scope_for(node):
        while node not in scope_of:
            node = parents[node]
        return scope_of[node]

    def report(node, kind):
        findings.append((node.lineno, scope_for(node).qualname, kind))

    def target_of(node):
        dotted = _dotted(node)
        if dotted is None:
            return None
        root, attributes = dotted
        target = scope_for(node).resolve(root, node.lineno)
        return ".".join([target] + attributes) if target else None

    def shift_of(node):
        if isinstance(node, ast.BinOp) and isinstance(
            node.op, (ast.RShift, ast.LShift)
        ):
            return node.left
        if isinstance(node, ast.Call) and node.args:
            if target_of(node.func) in SHIFT_FUNCTIONS:
                return node.args[0]
        return None

    def check_import(node, name):
        imports.append((node.lineno, name))
        if _is_stochastic(name):
            report(node, "stochastic import")
        elif name.split(".")[0] in HASH_MODULES:
            report(node, "hash library")

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                check_import(node, alias.name)
        elif isinstance(node, ast.ImportFrom):
            base = _absolute(node.module or "", node.level, package)
            names = [base] + [f"{base}.{alias.name}" for alias in node.names]
            imports.extend((node.lineno, name) for name in names)
            if any(map(_is_stochastic, names)):
                report(node, "stochastic import")
            elif base.split(".")[0] in HASH_MODULES:
                report(node, "hash library")
        elif isinstance(node, (ast.Name, ast.Attribute)) and isinstance(
            node.ctx, ast.Load
        ):
            parent = parents.get(node)
            if isinstance(parent, ast.Attribute) and parent.value is node:
                continue  # Only the whole chain counts.
            target = target_of(node)
            if target is None:
                continue
            kind = _classify(target)
            if kind:
                report(node, kind)
            elif target.startswith(root_package):
                references.append((node.lineno, scope_for(node).qualname, target))
        if isinstance(node, ast.Call):
            func = node.func
            called = target_of(func)
            first = _literal(node.args[0]) if node.args else None
            if called in DYNAMIC_IMPORTS and first:
                if first.startswith("."):
                    keywords = {k.arg: _literal(k.value) for k in node.keywords}
                    level = len(first) - len(first.lstrip("."))
                    first = _absolute(first.lstrip("."), level, keywords.get("package"))
                check_import(node, first)
            if called == "builtins.getattr" and len(node.args) >= 2:
                owner = target_of(node.args[0])
                attribute = _literal(node.args[1])
                kind = (
                    _classify(f"{owner}.{attribute}") if owner and attribute else None
                )
                if kind:
                    report(node, kind)
            if called in XOR_FUNCTIONS and len(node.args) == 2:
                if _is_xorshift(*node.args, shift_of):
                    report(node, "xorshift")
            if called in MOD_FUNCTIONS and node.args and _reads_an_id(node.args[0]):
                report(node, "id modulo")
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
        elif isinstance(node, (ast.BinOp, ast.AugAssign)):
            left = node.left if isinstance(node, ast.BinOp) else node.target
            right = node.right if isinstance(node, ast.BinOp) else node.value
            if isinstance(node.op, ast.BitXor) and _is_xorshift(left, right, shift_of):
                report(node, "xorshift")
            if isinstance(node.op, ast.Mod) and _reads_an_id(left):
                report(node, "id modulo")
    functions = [node.name for node in tree.body if isinstance(node, FUNCTION_NODES)]
    return Analysis(module, findings, references, functions, imports)


def helper_calls(analysis: Analysis, helpers) -> list:
    """(line, scope, "draw helper call") for each use of a draw helper."""
    return [
        (line, scope, "draw helper call")
        for line, scope, target in analysis.references
        if _matches(target, helpers)
    ]


def draw_helpers(analyses: dict, exempt: dict) -> set:
    """Top-level functions with a finding ``exempt`` does not cover.

    A function that uses one of them is one too, so this is a fixed point
    over the package.
    """
    helpers = set()
    while True:
        added = set()
        for relative, analysis in analyses.items():
            allowed = exempt.get(relative, {})
            counted = Counter(
                (scope, kind)
                for _, scope, kind in analysis.findings
                + helper_calls(analysis, helpers)
            )
            for name in analysis.functions:
                target = f"{analysis.module}.{name}"
                if target not in helpers and any(
                    count > allowed.get(key, 0)
                    for key, count in counted.items()
                    if key[0] == name or key[0].startswith(name + ".")
                ):
                    added.add(target)
        if not added:
            return helpers
        helpers |= added


def draw_findings(source: str, filename: str = "<string>", exempt=None) -> list:
    """(line, enclosing scope, kind) for every draw pattern in ``source``.

    ``exempt`` is the file's EXEMPT entries, which decide which of its
    functions are draw helpers.
    """
    analysis = analyse(source, filename)
    helpers = draw_helpers({filename: analysis}, {filename: exempt or {}})
    return sorted(analysis.findings + helper_calls(analysis, helpers))


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
    """(relative path, module name, package name, path) of every module."""
    for path in sorted(PACKAGE.rglob("*.py")):
        if TESTS in path.parents:
            continue
        relative = path.relative_to(PACKAGE).as_posix()
        dotted = f"{PACKAGE.name}.{relative.removesuffix('.py').replace('/', '.')}"
        if dotted.endswith(".__init__"):
            module = dotted.removesuffix(".__init__")
            yield relative, module, module, path
        else:
            yield relative, dotted, dotted.rsplit(".", 1)[0], path


def module_star_exports(paths: dict):
    """A function giving the names ``from <module> import *`` binds.

    ``paths`` maps package module names to (package name, path). Each
    module's public top-level names map to what they refer to, following its
    own imports and star imports.
    """
    exports = {}

    def star_exports(module):
        if module in STAR_EXPORTS or module not in paths:
            return STAR_EXPORTS.get(module, {})
        if module in exports:
            return exports[module]
        exports[module] = {}  # A cycle sees what has been bound so far.
        package, path = paths[module]
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        names = exports[module]
        public = None
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                names[node.name] = f"{module}.{node.name}"
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split(".")[0]
                    names[alias.asname or root] = alias.name if alias.asname else root
            elif isinstance(node, ast.ImportFrom):
                base = _absolute(node.module or "", node.level, package)
                for alias in node.names:
                    if alias.name == "*":
                        names.update(star_exports(base))
                    else:
                        names[alias.asname or alias.name] = f"{base}.{alias.name}"
            elif isinstance(node, (ast.Assign, ast.AnnAssign)):
                targets = (
                    node.targets if isinstance(node, ast.Assign) else [node.target]
                )
                dotted = _dotted(node.value) if node.value is not None else None
                for target in targets:
                    for name in ast.walk(target):
                        if isinstance(name, ast.Name):
                            names[name.id] = None
                    if isinstance(target, ast.Name) and dotted:
                        # name = other.chain, with other bound above.
                        root, attributes = dotted
                        if names.get(root):
                            names[target.id] = ".".join([names[root]] + attributes)
                    if isinstance(target, ast.Name) and target.id == "__all__":
                        try:
                            public = set(ast.literal_eval(node.value))
                        except ValueError:
                            public = None
        exports[module] = {
            name: target
            for name, target in names.items()
            if (name in public if public is not None else not name.startswith("_"))
        }
        return exports[module]

    return star_exports


class PackageScan(NamedTuple):
    counts: dict
    helpers: set
    imports: dict
    star_exports: object


@cache
def package_scan() -> PackageScan:
    """Every module analysed once per test session."""
    modules = list(package_modules())
    paths = {module: (package, path) for _, module, package, path in modules}
    star_exports = module_star_exports(paths)
    analyses = {
        relative: analyse(
            path.read_text(encoding="utf-8"), relative, module, package, star_exports
        )
        for relative, module, package, path in modules
    }
    helpers = draw_helpers(analyses, EXEMPT)
    counts = count_findings(
        {
            relative: analysis.findings + helper_calls(analysis, helpers)
            for relative, analysis in analyses.items()
        }
    )
    imports = {relative: analysis.imports for relative, analysis in analyses.items()}
    return PackageScan(counts, helpers, imports, star_exports)


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
        # Aliases, star imports and scopes.
        ("import numpy as np\nxp = np\nxp.random.uniform()\n", "random source"),
        ("r = np.random\ndef f():\n    return r.uniform()\n", "random source"),
        ("xp, k = np, 1\nxp.random.uniform()\n", "random source"),
        ("def f(xp=np):\n    return xp.random.uniform()\n", "random source"),
        ("from numpy import *\nrandom.uniform()\n", "random source"),
        ("getattr(np, 'random').uniform()\n", "random source"),
        (
            "import numpy as np\n"
            "def f():\n"
            "    return [np for np in np.random.uniform(size=2)]\n",
            "random source",
        ),
        ("if (r := np.random):\n    r.uniform()\n", "random source"),
        ("import importlib\nimportlib.import_module('random')\n", "stochastic import"),
        ("__import__('numpy.random')\n", "stochastic import"),
        ("from importlib import import_module as load\nload('zlib')\n", "hash library"),
        # Hashes.
        ('key = hash("x")\n', "builtin hash"),
        ("keys = map(hash, names)\n", "builtin hash"),
        ("import builtins\nbuiltins.hash(1)\n", "builtin hash"),
        (
            "class A:\n    hash = 1\n    def m(self, x):\n        return hash(x)\n",
            "builtin hash",
        ),
        ("import hashlib\n", "hash library"),
        ("from zlib import crc32\n", "hash library"),
        ("import hashlib\ndef f(b):\n    return hashlib.sha256(b)\n", "hash use"),
        ("from zlib import crc32\ncrc32(b'x') % 12\n", "hash use"),
        ("pd.util.hash_pandas_object(df)\n", "hash use"),
        ("m = np.uint64(0x94D049BB133111EB)\n", "hash constant"),
        ("gamma = 11400714819323198485\n", "hash constant"),
        ("h = 0xCBF29CE484222325\n", "hash constant"),
        ("x = x ^ (x >> 30)\n", "xorshift"),
        ("x = (x << 13) ^ x\n", "xorshift"),
        ("x ^= x >> 30\n", "xorshift"),
        ("x = np.bitwise_xor(x, np.right_shift(x, 30))\n", "xorshift"),
        # Sampling and ids.
        ("df = df.sample(frac=0.5, random_state=1)\n", "sampling call"),
        ("df = df.sample(5)\n", "sampling call"),
        ("rng.shuffle(values)\n", "sampling call"),
        ("pick = rng.choice(5)\n", "sampling call"),
        ("month = person_id % 12\n", "id modulo"),
        ('half = person("person_id", period) % 2\n', "id modulo"),
        ("person_id %= 12\n", "id modulo"),
        ("month = np.mod(person_id, 12)\n", "id modulo"),
        ("month, _ = divmod(person_id, 12)\n", "id modulo"),
        # A call of a function that draws.
        (
            "def mix(x):\n    return x ^ (x >> 3)\ndef f(x):\n    return mix(x)\n",
            "draw helper call",
        ),
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
        # A function sees the module's later bindings when it runs.
        "def f(x):\n    return hash(x)\ndef hash(x):\n    return x\n",
        "def f(hash):\n    return hash(1)\n",
        "class A:\n    def hash(self):\n        return 1\n    def m(self):\n"
        "        return self.hash()\n",
        '"""np.random.seed is banned"""\nlabel = "np.random"\n',
        "obj.random_seed\nobj.sample()\n",
        "months = np.ceil(weeks * 12 / 52)\nposition = (month - 1 - start) % 12\n",
        "flags = x ^ y\nbits = x >> 3\nbig = 0xFFFFFFFFFFFFFFFF\n",
        "rank = person.get_rank(person.household, person_id)\n",
        "import numpy as np\nnp.random_like = 1\nvalue = np.where(a, b, c)\n",
        "def f():\n    np = object()\n    return np.random\n",
        "xs = [random for random in range(3)]\n",
        "xp = object()\nxp.random.uniform()\n",
        "getattr(np, 'where')(a, b, c)\n",
        "import importlib\nimportlib.import_module('numpy')\n",
        "def helper(x):\n    return x + 1\ndef f(x):\n    return helper(x)\n",
    ],
)
def test_detector_skips_deterministic_code(source):
    assert draw_findings(source) == []


def test_draw_helpers_are_followed_through_calls():
    source = (
        "def mix(x):\n"
        "    return x ^ (x >> 3)\n"
        "def month(x):\n"
        "    return mix(x) % 12\n"
        "def formula(x):\n"
        "    return month(x) + 1\n"
    )
    found = {(scope, kind) for _, scope, kind in draw_findings(source)}
    assert ("month", "draw helper call") in found
    assert ("formula", "draw helper call") in found
    # A function whose findings are exempt is not a draw helper.
    exempt = {("mix", "xorshift"): 1}
    found = {(scope, kind) for _, scope, kind in draw_findings(source, exempt=exempt)}
    assert found == {("mix", "xorshift")}


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


def test_reusing_an_allowed_hash_or_draw_spends_an_occurrence():
    checksum = (
        "import hashlib\n"
        "def checksum(data):\n"
        "    return hashlib.sha256(data).hexdigest()\n"
    )
    exempt = {("<module>", "hash library"): 1, ("checksum", "hash use"): 1}

    def check(source, ratchet=None):
        findings = draw_findings(source, "m.py", exempt=exempt)
        counted = count_findings({"m.py": findings})
        return check_allowlists(counted, {"m.py": ratchet or {}}, {"m.py": exempt})

    assert check(checksum) == ([], [])
    # A new function hashing ids through the exempt import fails.
    reuse = checksum + (
        "def draw(person_id):\n"
        "    return hashlib.sha256(bytes(person_id)).digest()[0] % 12\n"
    )
    violations, _ = check(reuse)
    assert any("in draw: hash use" in violation for violation in violations)
    # So does a new call of a ratcheted draw.
    legacy = checksum + (
        "def legacy(x):\n"
        "    return x ^ (x >> 3)\n"
        "def stored(x):\n"
        "    return legacy(x)\n"
    )
    ratchet = {("legacy", "xorshift"): 1, ("stored", "draw helper call"): 1}
    assert check(legacy, ratchet) == ([], [])
    violations, _ = check(legacy + "def more(x):\n    return legacy(x)\n", ratchet)
    assert any("in more: draw helper call" in violation for violation in violations)


def test_star_imports_bind_the_imported_names():
    def star_exports(module):
        return {"draws": "numpy.random"} if module == "pkg.api" else {}

    source = "from pkg.api import *\ndraws.uniform()\n"
    found = analyse(source, star_exports=star_exports).findings
    assert [kind for _, _, kind in found] == ["random source"]
    # The package's model_api passes on core's numpy and its own helpers.
    exports = package_scan().star_exports("policyengine_us.model_api")
    assert exports["np"] == "numpy"
    assert exports["all_of_variables"] == "policyengine_us.model_api.all_of_variables"


def test_transitional_start_month_hash_is_a_draw_helper():
    module = (
        "policyengine_us.variables.gov.usda.snap.eligibility.work_requirements."
        "is_receiving_unemployment_compensation"
    )
    helpers = package_scan().helpers
    assert f"{module}.legacy_start_month_index" in helpers
    assert f"{module}.stored_start_month_index" in helpers
    assert f"{module}.situation_start_month_index" not in helpers
    assert "policyengine_us.system._file_sha256" not in helpers


def test_package_draws_nothing_outside_the_allowlists():
    violations, _ = check_allowlists(package_scan().counts, RATCHET, EXEMPT)
    assert not violations, (
        "The model must not draw, sample, shuffle or hash entities to a "
        "pseudo-random value while a simulation is built or run "
        "(policyengine-core#500). Draw in the dataset build and store the "
        "draw as an input variable; the formula then compares it with the "
        "rule, so a rate stays reformable. Draw patterns found:\n"
        + "\n".join(violations)
    )


def test_allowlist_entries_still_match():
    _, stale = check_allowlists(package_scan().counts, RATCHET, EXEMPT)
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


def _is_offline(name: str) -> bool:
    return _matches(name, OFFLINE_MODULES)


@pytest.mark.parametrize(
    "source",
    [
        "import policyengine_us.tools.taxsim.generate_taxsim_tests\n",
        "from policyengine_us.tools.taxsim import generate_taxsim_tests\n",
        "from .taxsim import generate_taxsim_tests\n",
        "import importlib\n"
        "importlib.import_module('policyengine_us.tools.taxsim.generate_taxsim_tests')\n",
        "from importlib import import_module as load\n"
        "load('.taxsim', package='policyengine_us.tools')\n",
        "__import__('policyengine_us.tools.taxsim')\n",
    ],
)
def test_offline_import_check_sees_each_import_form(source):
    imports = analyse(source, package="policyengine_us.tools").imports
    assert any(_is_offline(name) for _, name in imports)


def test_model_never_imports_offline_modules():
    importers = [
        f"{relative}:{line}"
        for relative, module, _, _ in package_modules()
        if not _is_offline(module)
        for line, name in package_scan().imports[relative]
        if _is_offline(name)
    ]
    assert not importers, (
        "Offline modules are exempt from the draw check only because the "
        "model never imports them:\n" + "\n".join(importers)
    )
