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
simulation code, data loading, uprating and tools). A name resolves to
everything it may refer to where it is used: the targets of every binding
that may be the one read, in each scope Python looks in, so the scan errs
toward reporting. Bindings come from imports, named imports and re-exports
followed across the package, star imports, assignments of a name or
attribute chain (``xp = np``, also in tuples), default arguments, ``global``
and ``nonlocal`` (the nearest enclosing function that binds the name,
wherever in its body), functions, lambdas and comprehensions. An attribute of
a package module, or of a module EXTERNAL_EXPORTS maps, is what that module
binds under the name, so ``api.np.random`` is numpy's random module where
``api`` is ``policyengine_core.model_api``. No code sees the names a class
body it is nested in binds. A module or class body looks further out when no
binding is sure to have run before the use with no ``del`` or ``except ...
as`` cleanup that may come between (all are in an ``if``, loop, ``try``,
``with`` or ``match``, or the use comes first). A function may run as soon as
its ``def`` has run, so the scopes around it count only the bindings before
the ``def``, and every later deletion. A function's ``del`` of a name it
declares ``global`` runs whenever the function is called, so after the
``def`` it may come between any binding and any use. A class body, a
decorated function and a lambda may run before the statement that creates
them has bound its names (a decorator may call the function, and an
assignment's value may call a lambda in it), so code inside them doesn't
take those bindings as sure.
So ``from numpy import random as r`` followed by ``r.random(3)`` is caught,
as are ``xp = np`` followed by ``xp.random.uniform()``, ``from
policyengine_us.model_api import np as lib`` followed by
``lib.random.uniform()``, and a ``try: import numpy as lib`` with a
fallback, while a local variable called ``random`` is not. A star import of
a package module binds its ``__all__`` (built from string literals with
``=``, ``+``, ``+=``, ``append``, ``extend`` or ``insert``; any other
``__all__`` exports every name) or, without one, every name it binds
without a leading underscore. EXTERNAL_EXPORTS lists the names numpy and
``policyengine_core.model_api`` bind where they matter here; ``np``,
``numpy`` and ``pd`` are bound to numpy and pandas wherever nothing else
binds them. Reported, as (file, enclosing function or class, kind):
- ``stochastic import``: importing ``random``, ``secrets`` or
  ``numpy.random`` (or anything from them), including through
  ``importlib.import_module`` or ``__import__`` with literal arguments,
  positional or keyword (``package``, ``fromlist`` and ``level`` too);
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
- ``draw helper call``: a use, under any name it is imported or re-exported
  as, of a top-level function of the package (one defined in an ``if`` or
  ``try`` too) whose body has a finding EXEMPT does not cover, or that
  itself uses such a function, so that calling an existing draw again also
  counts.

This is a ratchet over recognised patterns, not a proof that no
hand-written draw exists. It does not follow ``eval`` or ``exec``, imports
of a computed name, values reached through objects or containers
(``self.r = np.random`` is caught where ``np.random`` is read; a later
``self.r.uniform()`` is not), the values calls return (``r =
importlib.import_module("random")`` is caught at the import; a later
``r.random()`` is not), names ``match`` patterns capture, or methods as draw
helpers. A lookup that nests deeper than MAX_RESOLUTION_DEPTH fails the scan
rather than passing unresolved.

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
from itertools import permutations
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

# Names modules outside the package bind, where they matter here, for star
# and named imports alike. numpy's __all__ includes its random module.
EXTERNAL_EXPORTS = {
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
# Statements whose bodies may not run, so a binding inside may not happen.
COMPOUND_NODES = (
    ast.If,
    ast.For,
    ast.AsyncFor,
    ast.While,
    ast.Try,
    ast.TryStar,
    ast.With,
    ast.AsyncWith,
    ast.Match,
)
# Lookups nested deeper than this are cut, and the package scan fails
# (test_package_lookups_stay_within_the_depth_limit).
MAX_RESOLUTION_DEPTH = 64
# What ``from module import *`` binds when the module has no __all__, and
# when its __all__ is built in a way this scan does not evaluate.
DEFAULT_PUBLIC = "names without a leading underscore"
EVERY_NAME = "every name"


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


def _literal(node) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _targets(target) -> set:
    """The dotted names a binding's target may be."""
    if target is None:
        return set()
    if isinstance(target, str):
        return {target}
    return set(target.targets())


class _Alias:
    """A name bound, at ``line``, to another name or attribute chain."""

    def __init__(self, scope, value, line):
        self.scope = scope
        self.root, self.attributes = _dotted(value)
        self.line = line

    def targets(self):
        # The value is evaluated where and when the binding is made.
        roots = self.scope.modules.guarded(
            self,
            frozenset(),
            lambda: frozenset(self.scope.resolve(self.root, self.line)),
        )
        return self.scope.modules.expand_all(
            ".".join([root] + self.attributes) for root in roots
        )


class _Scope:
    """One namespace: a module, class, function, lambda or comprehension."""

    def __init__(self, kind, qualname, parent, modules, line=None):
        self.kind = kind
        self.qualname = qualname
        self.parent = parent
        self.modules = modules
        # Where the scope starts: a function's def, for instance.
        self.line = line
        # name -> [(line, target, conditional)]. The target is what the name
        # refers to (a module, function or other import), an _Alias to
        # resolve, or None for a value. A conditional binding
        # (in an if, loop, try, with or match, or a deletion) may not happen.
        self.bindings = {}
        # name -> [line] of each del or except ... as cleanup that may unbind
        # it.
        self.deletions = {}
        # name -> [line] of each def whose function may unbind it when
        # called, which may be at any time after that line.
        self.deletions_after = {}
        # For a scope that may run before the statement creating it has bound
        # its names (a class body, a decorated function, a lambda), that
        # statement's (first line, last line).
        self.unfinished = None
        # (line, module, conditional) for each star import.
        self.stars = []
        # Names a global or nonlocal statement gives to another scope.
        self.declared = {}
        # For a function or lambda, the names Python makes local to it.
        self.local_names = frozenset()

    def bind(self, name, line, target=None, conditional=False):
        owner = self.declared.get(name)
        if owner is not None:
            # Bound in that scope whenever this one runs, which may be never.
            return owner.bind(name, line, target, conditional=True)
        self.bindings.setdefault(name, []).append((line, target, conditional))

    def delete(self, name, line):
        """Record that ``name`` may be unbound at ``line``."""
        self.bind(name, line, None, conditional=True)
        owner = self.declared.get(name, self)
        # A deletion in a function, of a name another scope binds, happens
        # when the function is called: in the owner's time, any time after
        # the def of the outermost function between them.
        called_after = None
        scope = self
        while scope is not owner:
            if scope.kind in ("function", "lambda"):
                called_after = scope.line
            scope = scope.parent
        if called_after is None:
            owner.deletions.setdefault(name, []).append(line)
        else:
            owner.deletions_after.setdefault(name, []).append(called_after)

    def own(self, name, line, deferred, unfinished=()):
        """(targets, bound, falls through) for ``name`` in this scope alone.

        The use is at ``line`` or, with ``deferred``, at any time after it;
        a None line is once the scope has run. A binding within one of the
        ``unfinished`` (first line, last line) spans may not have happened
        yet.
        """
        entries = [(entry[0], entry[2]) for entry in self.bindings.get(name, [])]
        targets = set()
        for _, target, _ in self.bindings.get(name, []):
            targets |= _targets(target)
        for star_line, base, conditional in self.stars:
            provided = self.modules.star_binds(base, name)
            if provided is not None:
                targets |= provided
                entries.append((star_line, conditional))
        if not entries:
            return targets, False, True
        if self.kind not in ("module", "class"):
            # A name bound anywhere in a function is local to all of it.
            return targets, True, False
        # A module or class body looks further out unless a binding is sure
        # to have run before the use, with no deletion that may come between.
        deletions = self.deletions.get(name, [])
        deletions_after = self.deletions_after.get(name, [])

        def holds(bound_line):
            if deferred or line is None:
                return (
                    (line is None or bound_line <= line)
                    and all(deleted < bound_line for deleted in deletions)
                    and not deletions_after
                )
            return (
                bound_line < line
                and not any(bound_line <= deleted <= line for deleted in deletions)
                and not any(after <= line for after in deletions_after)
            )

        sure = [
            entry_line
            for entry_line, conditional in entries
            if not conditional
            and not any(first <= entry_line <= last for first, last in unfinished)
        ]
        return targets, True, not any(map(holds, sure))

    def resolve(self, name, line=None, deferred=False) -> set:
        """Every dotted target ``name`` may refer to at ``line``.

        The answer errs toward reporting: the targets of every binding that
        may be the one read, in each scope Python looks in until a binding is
        sure to hold. ``deferred`` says the code may run at any time after
        ``line``.
        """
        targets = set()
        owner = self.declared.get(name)
        scope, first = self, True
        unfinished = []
        while scope is not None:
            if scope is owner:
                owner = None
            # A global or nonlocal name skips the scopes up to the one it
            # names, and no code nested in a class body sees the names it
            # binds.
            if owner is None and (first or scope.kind != "class"):
                found, bound, falls = scope.own(name, line, deferred, unfinished)
                targets |= found
                if bound and not falls:
                    return targets
            if scope.unfinished is not None:
                # It may run before its statement's bindings have happened.
                unfinished.append(scope.unfinished)
            if scope.kind in ("function", "lambda"):
                # A function may run as soon as its def has run, so the
                # scopes around it are read as of the def, and any later
                # deletion counts.
                line, deferred = scope.line, True
            first = False
            scope = scope.parent
        if name in UNBOUND_NAMES:
            targets.add(UNBOUND_NAMES[name])
        return targets


def _comprehension_walrus_targets(node) -> set:
    """Names a walrus binds anywhere in a comprehension, which Python binds
    in the function around it. A lambda inside is a scope of its own, apart
    from its defaults."""
    targets = set()
    stack = [node]
    while stack:
        child = stack.pop()
        if isinstance(child, ast.NamedExpr):
            targets.add(child.target.id)
        if isinstance(child, ast.Lambda):
            stack.extend(child.args.defaults)
            stack.extend(d for d in child.args.kw_defaults if d)
            continue
        stack.extend(ast.iter_child_nodes(child))
    return targets


def _function_locals(node) -> frozenset:
    """The names Python makes local to a function or lambda, wherever its
    body binds them: its parameters and every name bound outside nested
    scopes, less those a global or nonlocal statement sends elsewhere."""
    arguments = node.args
    parameters = arguments.posonlyargs + arguments.args + arguments.kwonlyargs
    parameters += [arguments.vararg, arguments.kwarg]
    names = {argument.arg for argument in parameters if argument is not None}
    declared = set()
    stack = list(node.body if isinstance(node.body, list) else [node.body])
    while stack:
        child = stack.pop()
        if isinstance(child, (ast.Global, ast.Nonlocal)):
            declared.update(child.names)
            continue
        if isinstance(child, FUNCTION_NODES + (ast.ClassDef, ast.Lambda)):
            # Only its name, decorators, defaults, annotations and bases are
            # this scope's. Up to 3.13 annotations are evaluated here, so a
            # walrus in one binds here; 3.14 defers them and refuses a walrus
            # in one, so the earlier rule covers both.
            if not isinstance(child, ast.Lambda):
                names.add(child.name)
            stack.extend(getattr(child, "decorator_list", []))
            if isinstance(child, ast.ClassDef):
                stack.extend(child.bases + [k.value for k in child.keywords])
            else:
                stack.extend(child.args.defaults)
                stack.extend(d for d in child.args.kw_defaults if d)
            if isinstance(child, FUNCTION_NODES):
                stack.extend([child.returns] if child.returns else [])
                stack.extend(
                    argument.annotation
                    for argument in ast.walk(child.args)
                    if isinstance(argument, ast.arg) and argument.annotation
                )
            continue
        if isinstance(child, COMPREHENSION_NODES):
            # Its loop variables are its own; a walrus binds here. Since 3.12
            # CPython inlines a list, set or dict comprehension (PEP 709; not a
            # generator expression), and a nested nonlocal of a loop
            # variable's name then names a cell here that only such nonlocals
            # set, not the binding further out that 3.11 and a generator
            # expression name. Following 3.11 keeps every value either can
            # read.
            names.update(_comprehension_walrus_targets(child))
            stack.append(child.generators[0].iter)
            continue
        if isinstance(child, ast.Name) and not isinstance(child.ctx, ast.Load):
            names.add(child.id)
        elif isinstance(child, (ast.Import, ast.ImportFrom)):
            names.update(
                (alias.asname or alias.name).split(".")[0]
                for alias in child.names
                if alias.name != "*"
            )
        elif isinstance(child, ast.ExceptHandler) and child.name:
            names.add(child.name)
        elif isinstance(child, (ast.MatchAs, ast.MatchStar)) and child.name:
            names.add(child.name)
        elif isinstance(child, ast.MatchMapping) and child.rest:
            names.add(child.rest)
        stack.extend(ast.iter_child_nodes(child))
    return frozenset(names - declared)


def _alias(scope, value, line):
    """What binding ``value`` at ``line`` binds: an _Alias of a name or chain."""
    if value is not None and _dotted(value) is not None:
        return _Alias(scope, value, line)
    return None


def _is_all(node) -> bool:
    return isinstance(node, ast.Name) and node.id == "__all__"


def _strings(node, current):
    """The set of strings ``node`` builds, with ``current`` as __all__."""
    if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        values = [_literal(element) for element in node.elts]
        return None if None in values else set(values)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left, right = _strings(node.left, current), _strings(node.right, current)
        return None if left is None or right is None else left | right
    if _is_all(node):
        return set(current)
    return None


def _public_names(tree):
    """What ``from module import *`` binds, from the module's ``__all__``.

    A frozenset of names, DEFAULT_PUBLIC without an ``__all__``, or
    EVERY_NAME for an ``__all__`` built other than from string literals with
    ``=``, ``+``, ``+=``, ``append``, ``extend`` and ``insert`` at the top
    level. Removals are ignored, which keeps more names than Python would.
    """
    uses = {node for node in ast.walk(tree) if _is_all(node)}
    if not uses:
        return DEFAULT_PUBLIC
    names, handled = set(), set()
    for statement in tree.body:
        value = None
        if isinstance(statement, (ast.Assign, ast.AnnAssign)):
            targets = (
                statement.targets
                if isinstance(statement, ast.Assign)
                else [statement.target]
            )
            if len(targets) == 1 and _is_all(targets[0]) and statement.value:
                value = _strings(statement.value, names)
                if value is None:
                    return EVERY_NAME
                names = value
        elif (
            isinstance(statement, ast.AugAssign)
            and _is_all(statement.target)
            and isinstance(statement.op, ast.Add)
        ):
            value = _strings(statement.value, names)
            if value is None:
                return EVERY_NAME
            names = names | value
        elif (
            isinstance(statement, ast.Expr)
            and isinstance(statement.value, ast.Call)
            and isinstance(statement.value.func, ast.Attribute)
            and _is_all(statement.value.func.value)
        ):
            method, args = statement.value.func.attr, statement.value.args
            if method == "append" and len(args) == 1 and _literal(args[0]):
                value = {_literal(args[0])}
            elif method == "insert" and len(args) == 2 and _literal(args[1]):
                value = {_literal(args[1])}
            elif method == "extend" and len(args) == 1:
                value = _strings(args[0], names)
            elif method == "remove":
                value = set()
            if value is None:
                return EVERY_NAME
            names = names | value
        if value is not None:
            handled |= {node for node in ast.walk(statement) if _is_all(node)}
    if uses - handled:
        return EVERY_NAME
    return frozenset(names)


class Modules:
    """The package's modules, built on demand, for names one imports from another.

    ``sources`` maps module names to (package name, a function returning the
    source). A lookup is a pure function of the sources: a cycle is cut
    where a lookup meets itself, and a result computed across a cut is not
    kept, so no answer depends on the order of lookups. A lookup nested
    deeper than ``max_depth`` is cut too, and recorded in ``exhausted``: a
    result kept from a shallower lookup could fill that cut in another order.
    """

    def __init__(self, sources: dict, external=None, max_depth=MAX_RESOLUTION_DEPTH):
        self.sources = sources
        self.external = EXTERNAL_EXPORTS if external is None else external
        self.max_depth = max_depth
        self.exhausted = set()
        self.tops = {}
        self.publics = {}
        self._memo = {}
        self._active = set()
        self._cuts = 0

    def top(self, module):
        if module not in self.tops:
            package, read = self.sources[module]
            tree = ast.parse(read(), filename=module)
            self.register(module, _build_scopes(tree, module, package, self)[0], tree)
        return self.tops[module]

    def register(self, module, top, tree):
        if module not in self.tops:
            self.tops[module] = top
            self.publics[module] = _public_names(tree)

    def guarded(self, key, cut, compute):
        """``compute()``, or ``cut`` where the lookup meets itself."""
        if key in self._memo:
            return self._memo[key]
        if key in self._active or len(self._active) > self.max_depth:
            if key not in self._active:
                self.exhausted.add(key)
            self._cuts += 1
            return cut
        self._active.add(key)
        cuts = self._cuts
        try:
            result = compute()
        finally:
            self._active.discard(key)
        if self._cuts == cuts and not isinstance(key, _Alias):
            self._memo[key] = result
        return result

    def binding(self, module, name):
        """(bound, targets) for ``module``'s top-level ``name`` once it ran."""

        def compute():
            targets, bound, _ = self.top(module).own(name, None, True)
            return bound, frozenset(targets)

        return self.guarded(("binding", module, name), (False, frozenset()), compute)

    def expand(self, target, start=1) -> frozenset:
        """``target`` and what else it names, where a prefix of it at least
        ``start`` parts long is a package module or one ``external`` maps and
        the next part is a name that module binds.

        The binding's targets, expanded, replace that prefix and name, and
        only the rest is expanded further: a dotted name is both a module
        path and a chain of attributes, and ``a.b`` may bind ``b`` to a path
        through the submodule ``a.b``.
        """

        def compute():
            found = {target}
            parts = target.split(".")
            for index in range(start, len(parts)):
                base, name = ".".join(parts[:index]), parts[index]
                if base in self.sources:
                    bound = self.binding(base, name)[1]
                else:
                    mapped = self.external.get(base, {}).get(name)
                    bound = {mapped} if mapped else set()
                for head in self.expand_all(bound):
                    named = ".".join([head] + parts[index + 1 :])
                    if named != target:
                        found |= self.expand(named, len(head.split(".")))
            return frozenset(found)

        key = ("expand", target, start)
        return self.guarded(key, frozenset({target}), compute)

    def expand_all(self, targets) -> set:
        return set().union(*map(self.expand, targets))

    def star_binds(self, base, name):
        """What ``from base import *`` binds ``name`` to, or None."""
        if base not in self.sources:
            mapped = self.external.get(base, {}).get(name)
            return {mapped} if mapped else None
        self.top(base)
        public = self.publics[base]
        if public == DEFAULT_PUBLIC:
            exported = not name.startswith("_")
        else:
            exported = public == EVERY_NAME or name in public
        if not exported:
            return None
        bound, targets = self.binding(base, name)
        if bound:
            return set(targets)
        if isinstance(public, frozenset):
            return {f"{base}.{name}"}  # A submodule __all__ lists.
        return None


def _build_scopes(tree, module, package, modules):
    """(module scope, the innermost scope of every node) of ``tree``."""
    top = _Scope("module", "<module>", None, modules)
    scope_of = {}

    def assign(target, value, scope, conditional, evaluated_in=None):
        """Bind ``target`` in ``scope`` to ``value``, evaluated in
        ``evaluated_in`` (by default ``scope``)."""
        scope_of[target] = scope
        if isinstance(target, ast.Name):
            line = target.lineno
            alias = _alias(evaluated_in or scope, value, line)
            scope.bind(target.id, line, alias, conditional)
        elif (
            isinstance(target, (ast.Tuple, ast.List))
            and isinstance(value, (ast.Tuple, ast.List))
            and len(target.elts) == len(value.elts)
        ):
            for element, element_value in zip(target.elts, value.elts):
                assign(element, element_value, scope, conditional, evaluated_in)
        else:
            visit(target, scope, conditional)

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

    def declare(inner, body):
        """Send names a global or nonlocal statement in ``body`` names to
        the scope that binds them."""
        stack = list(body)
        while stack:
            node = stack.pop()
            if isinstance(node, ast.Global):
                for name in node.names:
                    inner.declared[name] = top
            elif isinstance(node, ast.Nonlocal):
                # The nearest enclosing function that makes the name local,
                # wherever in its body it binds it; class bodies are skipped.
                for name in node.names:
                    owner = inner.parent
                    while owner is not None and not (
                        owner.kind in ("function", "lambda")
                        and name in owner.local_names
                    ):
                        owner = owner.parent
                    if owner is not None:
                        inner.declared[name] = owner
            elif not isinstance(node, FUNCTION_NODES + (ast.ClassDef, ast.Lambda)):
                stack.extend(ast.iter_child_nodes(node))

    def visit_function(node, scope, conditional):
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
            visit(child, scope, conditional)
        name = getattr(node, "name", "<lambda>")
        if not isinstance(node, ast.Lambda):
            top_level = scope.parent is None
            target = f"{module}.{name}" if top_level else None
            scope.bind(name, node.lineno, target, conditional)
        qualname = name if scope.parent is None else f"{scope.qualname}.{name}"
        kind = "lambda" if isinstance(node, ast.Lambda) else "function"
        inner = _Scope(kind, qualname, scope, modules, node.lineno)
        if isinstance(node, ast.Lambda) or node.decorator_list:
            inner.unfinished = statement_span[-1]
        inner.local_names = _function_locals(node)
        body = node.body if isinstance(node.body, list) else [node.body]
        declare(inner, body)
        bind_arguments(inner, scope, node.args, node.lineno)
        for child in body:
            visit(child, inner)

    def visit_class(node, scope, conditional):
        for child in node.decorator_list + node.bases:
            visit(child, scope, conditional)
        for keyword in node.keywords:
            visit(keyword.value, scope, conditional)
        top_level = scope.parent is None
        target = f"{module}.{node.name}" if top_level else None
        scope.bind(node.name, node.lineno, target, conditional)
        qualname = node.name if top_level else f"{scope.qualname}.{node.name}"
        inner = _Scope("class", qualname, scope, modules, node.lineno)
        inner.unfinished = statement_span[-1]
        declare(inner, node.body)
        for child in node.body:
            visit(child, inner)

    def visit_comprehension(node, scope, conditional):
        # The first iterable is evaluated in the enclosing scope; the rest
        # in the comprehension's own, reported under the enclosing name.
        visit(node.generators[0].iter, scope, conditional)
        inner = _Scope("comprehension", scope.qualname, scope, modules, node.lineno)
        for index, generator in enumerate(node.generators):
            scope_of[generator] = inner
            if index:
                visit(generator.iter, inner)
            assign(generator.target, None, inner, False)
            for condition in generator.ifs:
                visit(condition, inner)
        if isinstance(node, ast.DictComp):
            elements = [node.key, node.value]
        else:
            elements = [node.elt]
        for element in elements:
            visit(element, inner)

    # (first line, last line) of each statement being visited, innermost
    # last; a definition's decorators are part of its statement.
    statement_span = [(1, 1)]

    def visit(node, scope, conditional=False):
        if not isinstance(node, ast.stmt):
            return visit_node(node, scope, conditional)
        lines = [node.lineno]
        lines += [d.lineno for d in getattr(node, "decorator_list", [])]
        statement_span.append((min(lines), node.end_lineno))
        try:
            return visit_node(node, scope, conditional)
        finally:
            statement_span.pop()

    def visit_node(node, scope, conditional):
        scope_of[node] = scope
        if isinstance(node, FUNCTION_NODES + (ast.Lambda,)):
            return visit_function(node, scope, conditional)
        if isinstance(node, ast.ClassDef):
            return visit_class(node, scope, conditional)
        if isinstance(node, COMPREHENSION_NODES):
            return visit_comprehension(node, scope, conditional)
        if isinstance(node, ast.Assign):
            visit(node.value, scope, conditional)
            for target in node.targets:
                assign(target, node.value, scope, conditional)
            return
        if isinstance(node, ast.AnnAssign):
            visit(node.annotation, scope, conditional)
            if node.value is not None:
                visit(node.value, scope, conditional)
            return assign(node.target, node.value, scope, conditional)
        if isinstance(node, ast.NamedExpr):
            visit(node.value, scope, conditional)
            # The target belongs to the scope around any comprehensions; the
            # value is evaluated where the expression is.
            owner = scope
            while owner.kind == "comprehension":
                owner = owner.parent
            return assign(node.target, node.value, owner, conditional, scope)
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.asname:
                    scope.bind(alias.asname, node.lineno, alias.name, conditional)
                else:
                    root = alias.name.split(".")[0]
                    scope.bind(root, node.lineno, root, conditional)
        elif isinstance(node, ast.ImportFrom):
            base = _absolute(node.module or "", node.level, package)
            for alias in node.names:
                if alias.name == "*":
                    scope.stars.append((node.lineno, base, conditional))
                else:
                    # A submodule or a name base binds: expand decides.
                    name = alias.asname or alias.name
                    scope.bind(name, node.lineno, f"{base}.{alias.name}", conditional)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            scope.bind(node.id, node.lineno, None, conditional)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Del):
            scope.delete(node.id, node.lineno)
        elif isinstance(node, ast.ExceptHandler) and node.name:
            # Python deletes the name when the handler ends.
            scope.bind(node.name, node.lineno, None, True)
            scope.delete(node.name, node.end_lineno)
        inside = conditional or isinstance(node, COMPOUND_NODES)
        for child in ast.iter_child_nodes(node):
            visit(child, scope, inside)

    visit(tree, top)
    return top, scope_of


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


def _argument(call, position, keyword):
    """The argument ``call`` passes at ``position`` or as ``keyword``."""
    if len(call.args) > position:
        return call.args[position]
    for passed in call.keywords:
        if passed.arg == keyword:
            return passed.value
    return None


def _dynamic_imports(call, called, package) -> list:
    """Absolute names a call of a dynamic import function imports, where its
    arguments are literals."""
    names = []
    if "importlib.import_module" in called:
        name = _literal(_argument(call, 0, "name"))
        relative_to = _literal(_argument(call, 1, "package"))
        if name and name.startswith("."):
            level = len(name) - len(name.lstrip("."))
            names.append(_absolute(name.lstrip("."), level, relative_to))
        elif name:
            names.append(name)
    if "builtins.__import__" in called:
        name = _literal(_argument(call, 0, "name"))
        level = _argument(call, 4, "level")
        level = level.value if isinstance(level, ast.Constant) else 0
        if name is not None and isinstance(level, int):
            base = _absolute(name, level, package) if level else name
            names.append(base)
            fromlist = _argument(call, 3, "fromlist")
            if isinstance(fromlist, (ast.List, ast.Tuple, ast.Set)):
                items = [_literal(item) for item in fromlist.elts]
                names += [f"{base}.{item}" for item in items if item]
    return names


class Analysis(NamedTuple):
    module: str
    # (line, enclosing scope, kind), without draw helper calls.
    findings: list
    # (line, enclosing scope, targets) for each use that may name something
    # in the package.
    references: list
    # Names of the module's top-level functions, also those defined in an
    # if or try.
    functions: list
    # (line, absolute module name) for each import, static or literal dynamic.
    imports: list


def analyse(
    source: str,
    filename: str = "<string>",
    module: str = "m",
    package: str | None = None,
    modules: Modules | None = None,
) -> Analysis:
    """Draw patterns, package references and imports of one module.

    ``modules`` resolves names imported from other package modules; without
    it the module stands alone.
    """
    tree = ast.parse(source, filename=filename)
    if modules is None:
        modules = Modules({module: (package, lambda: source)})
    top, scope_of = _build_scopes(tree, module, package, modules)
    modules.register(module, top, tree)
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

    def report_targets(node, targets):
        for kind in sorted({_classify(target) for target in targets} - {None}):
            report(node, kind)

    def targets_of(node) -> set:
        dotted = _dotted(node)
        if dotted is None:
            return set()
        root, attributes = dotted
        return modules.expand_all(
            ".".join([target] + attributes)
            for target in scope_for(node).resolve(root, node.lineno)
        )

    def shift_of(node):
        if isinstance(node, ast.BinOp) and isinstance(
            node.op, (ast.RShift, ast.LShift)
        ):
            return node.left
        if isinstance(node, ast.Call) and node.args:
            if targets_of(node.func) & SHIFT_FUNCTIONS:
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
            targets = targets_of(node)
            report_targets(node, targets)
            named = frozenset(t for t in targets if t.startswith(root_package))
            if named:
                references.append((node.lineno, scope_for(node).qualname, named))
        if isinstance(node, ast.Call):
            func = node.func
            called = targets_of(func)
            if called & DYNAMIC_IMPORTS:
                for name in _dynamic_imports(node, called, package):
                    check_import(node, name)
            if "builtins.getattr" in called and len(node.args) >= 2:
                attribute = _literal(node.args[1])
                if attribute:
                    owners = targets_of(node.args[0])
                    report_targets(
                        node,
                        modules.expand_all(f"{owner}.{attribute}" for owner in owners),
                    )
            if called & XOR_FUNCTIONS and len(node.args) == 2:
                if _is_xorshift(*node.args, shift_of):
                    report(node, "xorshift")
            if called & MOD_FUNCTIONS and node.args and _reads_an_id(node.args[0]):
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
    functions = [
        node.name
        for node in ast.walk(tree)
        if isinstance(node, FUNCTION_NODES) and scope_of.get(node) is top
    ]
    return Analysis(module, findings, references, functions, imports)


def helper_calls(analysis: Analysis, helpers) -> list:
    """(line, scope, "draw helper call") for each use of a draw helper."""
    return [
        (line, scope, "draw helper call")
        for line, scope, targets in analysis.references
        if any(_matches(target, helpers) for target in targets)
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


def _reader(path):
    return lambda: path.read_text(encoding="utf-8")


class PackageScan(NamedTuple):
    counts: dict
    helpers: set
    imports: dict
    modules: Modules


@cache
def package_scan() -> PackageScan:
    """Every module analysed once per test session."""
    listed = list(package_modules())
    modules = Modules(
        {module: (package, _reader(path)) for _, module, package, path in listed}
    )
    analyses = {
        relative: analyse(
            path.read_text(encoding="utf-8"), relative, module, package, modules
        )
        for relative, module, package, path in listed
    }
    helpers = draw_helpers(analyses, EXEMPT)
    counts = count_findings(
        {
            relative: analysis.findings + helper_calls(analysis, helpers)
            for relative, analysis in analyses.items()
        }
    )
    imports = {relative: analysis.imports for relative, analysis in analyses.items()}
    return PackageScan(counts, helpers, imports, modules)


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
        # A walrus in a comprehension binds outside it, to a value read inside.
        (
            "import numpy as np\n[(lib := np) for _ in [0]]\nlib.random.uniform()\n",
            "random source",
        ),
        # A name may refer to any binding that may be the one read.
        (
            "from policyengine_core.model_api import np as lib\nlib.random.uniform()\n",
            "random source",
        ),
        # An attribute of a module is what the module binds under the name.
        (
            "import policyengine_core.model_api as api\napi.np.random.uniform()\n",
            "random source",
        ),
        (
            "from policyengine_core import model_api\nmodel_api.np.random.uniform()\n",
            "random source",
        ),
        (
            "import policyengine_core.model_api as api\nlib = api.np\nlib.random.uniform()\n",
            "random source",
        ),
        (
            "import numpy as lib\n"
            "values = [lib.random.uniform() for _ in range(1)]\n"
            "lib = object()\n",
            "random source",
        ),
        (
            "import numpy as np\n"
            "class Outer:\n"
            "    np = object()\n"
            "    class Inner:\n"
            "        value = np.random.uniform()\n",
            "random source",
        ),
        (
            "class Outer:\n    hash = 1\n    class Inner:\n        key = hash('x')\n",
            "builtin hash",
        ),
        ("import numpy as lib; alias = lib; alias.random.uniform()\n", "random source"),
        (
            "try:\n"
            "    import numpy as lib\n"
            "except ImportError:\n"
            "    lib = None\n"
            "lib.random.uniform()\n",
            "random source",
        ),
        (
            "def setup():\n"
            "    global lib\n"
            "    import numpy as lib\n"
            "def f():\n"
            "    return lib.random.uniform()\n",
            "random source",
        ),
        (
            "def outer():\n"
            "    lib = None\n"
            "    def setup():\n"
            "        nonlocal lib\n"
            "        import numpy as lib\n"
            "    return lib.random.uniform()\n",
            "random source",
        ),
        # A global name skips the functions between it and the module.
        (
            "import numpy as lib\n"
            "def outer():\n"
            "    lib = None\n"
            "    def inner():\n"
            "        global lib\n"
            "        return lib.random.random()\n"
            "    return inner\n",
            "random source",
        ),
        # nonlocal names the nearest function that binds the name, not the
        # nearest function, and wherever in its body the binding is.
        (
            "def outer():\n"
            "    import numpy as lib\n"
            "    def middle():\n"
            "        def inner():\n"
            "            nonlocal lib\n"
            "            lib.random.random()\n"
            "            lib = None\n"
            "        inner()\n"
            "    middle()\n",
            "random source",
        ),
        (
            "def outer():\n"
            "    def middle():\n"
            "        def inner():\n"
            "            nonlocal lib\n"
            "            lib = None\n"
            "            return lib.random.random()\n"
            "        return inner\n"
            "    import numpy as lib\n"
            "    return middle\n",
            "random source",
        ),
        # A walrus in a nested function's annotation binds in the function
        # around it, so middle binds lib and inner reads numpy.
        (
            "import numpy as np\n"
            "def outer():\n"
            "    lib = None\n"
            "    def middle():\n"
            "        def annotated(x: (lib := np)):\n"
            "            pass\n"
            "        def inner():\n"
            "            nonlocal lib\n"
            "            return lib.random.random()\n"
            "        return inner\n"
            "    return middle\n",
            "random source",
        ),
        (
            "import numpy as np\n"
            "def outer():\n"
            "    lib = None\n"
            "    def middle():\n"
            "        def annotated() -> (lib := np):\n"
            "            pass\n"
            "        def inner():\n"
            "            nonlocal lib\n"
            "            return lib.random.random()\n"
            "        return inner\n"
            "    return middle\n",
            "random source",
        ),
        # A walrus in a lambda binds in the lambda, even inside a
        # comprehension, so middle doesn't bind lib.
        (
            "def outer():\n"
            "    import numpy as lib\n"
            "    def middle():\n"
            "        [(lambda: (lib := None)) for marker in ()]\n"
            "        def inner():\n"
            "            nonlocal lib\n"
            "            lib.random.random()\n"
            "            lib = None\n"
            "        inner()\n"
            "    middle()\n",
            "random source",
        ),
        ("if flag:\n    hash = str\nkey = hash('x')\n", "builtin hash"),
        ("key = hash('x')\nhash = str\n", "builtin hash"),
        # A deletion, or the end of an except clause, may unbind a shadow.
        ("hash = str\ndel hash\nkey = hash('x')\n", "builtin hash"),
        (
            "class A:\n    hash = str\n    del hash\n    key = hash('x')\n",
            "builtin hash",
        ),
        (
            "hash = str\n"
            "try:\n"
            "    pass\n"
            "except ValueError as hash:\n"
            "    pass\n"
            "key = hash('x')\n",
            "builtin hash",
        ),
        (
            "hash = str\n"
            "def clear():\n"
            "    global hash\n"
            "    del hash\n"
            "clear()\n"
            "key = hash('x')\n",
            "builtin hash",
        ),
        # A function's del of a global may run after a later binding.
        (
            "def clear():\n"
            "    global hash\n"
            "    del hash\n"
            "hash = str\n"
            "clear()\n"
            "key = hash('x')\n",
            "builtin hash",
        ),
        (
            "def clear():\n"
            "    global hash\n"
            "    if flag:\n"
            "        del hash\n"
            "hash = str\n"
            "clear()\n"
            "key = hash('x')\n",
            "builtin hash",
        ),
        (
            "def outer():\n"
            "    def clear():\n"
            "        global hash\n"
            "        del hash\n"
            "    return clear\n"
            "hash = str\n"
            "outer()()\n"
            "def consumer(value):\n"
            "    return hash(value)\n",
            "builtin hash",
        ),
        # Code may run before the statement creating it binds its names: a
        # decorator may call the function, a class body runs before its
        # name is bound, and an assignment's value may call a lambda in it.
        (
            "def eager(f):\n"
            "    return f('x')\n"
            "@eager\n"
            "def hash(value):\n"
            "    return hash(value)\n",
            "builtin hash",
        ),
        ("class hash:\n    answer = hash('x')\n", "builtin hash"),
        ("hash = (lambda value: hash(value))('x')\n", "builtin hash"),
        # A function may run before a later binding, or after a deletion.
        (
            "def consumer(value):\n"
            "    return hash(value)\n"
            "answer = consumer('x')\n"
            "hash = str\n",
            "builtin hash",
        ),
        ("hash = str\ndef f(x):\n    return hash(x)\ndel hash\n", "builtin hash"),
        ("import importlib\nimportlib.import_module('random')\n", "stochastic import"),
        (
            "import importlib\nimportlib.import_module(name='random')\n",
            "stochastic import",
        ),
        ("__import__('numpy.random')\n", "stochastic import"),
        ("__import__('numpy', fromlist=['random'])\n", "stochastic import"),
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
        # A binding sure to run before a function's def hides the builtin
        # from its body; so does a binding after a deletion.
        "def hash(x):\n    return x\ndef f(x):\n    return hash(x)\n",
        "hash = str\nclass A:\n    def m(self, x):\n        return hash(x)\n",
        "hash = str\ndel hash\nhash = repr\nkey = hash('x')\n",
        "def f(x):\n    hash = str\n    del hash\n    return x\n",
        # Deleting a local leaves it unbound (UnboundLocalError); the
        # builtin stays hidden.
        "def f():\n    hash = str\n    del hash\n    return hash('x')\n",
        # Nothing can call an undecorated function before its def binds it.
        "def hash(x):\n    return hash(x - 1) if x else 0\nhash(3)\n",
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
        # A binding sure to have run hides the builtin.
        "hash = str\nkey = hash('x')\n",
        "class A:\n    hash = str\n    key = hash('x')\n",
        "def f():\n    hash = str\n    return hash('x')\n",
        # The walrus value is the comprehension's own np, not numpy.
        "import numpy as np\n[(lib := np) for np in [object()]]\nlib.random.uniform()\n",
        # nonlocal stops at the nearest function binding the name.
        "def outer():\n"
        "    import numpy as lib\n"
        "    def middle():\n"
        "        lib = object()\n"
        "        def inner():\n"
        "            nonlocal lib\n"
        "            return lib.random.random()\n"
        "        return inner\n"
        "    return middle\n",
        # A walrus in a lambda's default binds where the comprehension runs,
        # so in middle.
        "def outer():\n"
        "    import numpy as lib\n"
        "    def middle():\n"
        "        [(lambda x=(lib := None): x) for marker in ()]\n"
        "        def inner():\n"
        "            nonlocal lib\n"
        "            return lib.random.random()\n"
        "        return inner\n"
        "    return middle\n",
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


def _package_findings(sources: dict, order=None, exempt=None) -> dict:
    """{module: findings} of a package ``pkg`` given {module: source}.

    ``order`` is the order the modules are analysed in.
    """
    modules = Modules(
        {
            f"pkg.{name}": ("pkg", lambda source=source: source)
            for name, source in sources.items()
        }
    )
    analyses = {
        name: analyse(sources[name], f"{name}.py", f"pkg.{name}", "pkg", modules)
        for name in order or sources
    }
    helpers = draw_helpers(analyses, exempt or {})
    return {
        name: sorted(analysis.findings + helper_calls(analysis, helpers))
        for name, analysis in analyses.items()
    }


def _package_kinds(sources: dict, module: str = "user") -> list:
    return [kind for _, _, kind in _package_findings(sources)[module]]


def test_named_imports_and_reexports_resolve_to_what_they_name():
    api = "import numpy as lib\nfrom numpy import random as draws\n"
    user = (
        "from .api import lib\n"
        "lib.random.uniform()\n"
        "from .api import draws as d\n"
        "d.uniform()\n"
    )
    assert _package_kinds({"api": api, "user": user}) == ["random source"] * 2
    # A draw helper re-exported by name is still a draw helper.
    helper = "def mix(x):\n    return x ^ (x >> 3)\n"
    found = _package_findings(
        {
            "a": helper,
            "b": "from .a import mix\n",
            "c": "from .b import mix\ndef consumer(x):\n    return mix(x)\n",
        }
    )
    assert ("consumer", "draw helper call") in {(s, k) for _, s, k in found["c"]}


def test_module_attributes_resolve_to_what_the_module_binds():
    # A name passed on as an attribute of another module.
    sources = {
        "api": "import numpy as lib\n",
        "bridge": "from . import api\nlib = api.lib\n",
        "user": "from .bridge import lib\nlib.random.uniform()\n",
    }
    assert _package_kinds(sources) == ["random source"]
    # A draw helper reached as an attribute of a module that re-exports it.
    found = _package_findings(
        {
            "a": "def mix(x):\n    return x ^ (x >> 3)\n",
            "b": "from .a import mix\n",
            "c": "from . import b\ndef consumer(x):\n    return b.mix(x)\n",
        }
    )
    assert ("consumer", "draw helper call") in {(s, k) for _, s, k in found["c"]}


def test_a_package_that_rebinds_its_submodules_name_resolves():
    # Both __init__ files bind w to the function pkg.w.w defines, so the
    # attribute pkg.w is that function, though "pkg.w" also names a package
    # (as policyengine_us.reforms.congress.mcdonald_rivet does).
    sources = {
        "pkg": ("pkg", "from .w import w\n"),
        "pkg.w": ("pkg.w", "from .w import w\n"),
        "pkg.w.w": ("pkg.w", "def w(x):\n    return x ^ (x >> 3)\n"),
        "pkg.user": ("pkg", "import pkg\ndef consumer(x):\n    return pkg.w(x)\n"),
    }
    # This resolution needs depth 4. A low limit makes one that expands
    # pkg.w.w.w into ever longer paths fail fast, with a recorded cut,
    # instead of searching for minutes.
    modules = Modules(
        {
            module: (package, lambda source=source: source)
            for module, (package, source) in sources.items()
        },
        max_depth=5,
    )
    analyses = {
        module: analyse(source, f"{module}.py", module, package, modules)
        for module, (package, source) in sources.items()
    }
    helpers = draw_helpers(analyses, {})
    assert "pkg.w.w.w" in helpers
    calls = helper_calls(analyses["pkg.user"], helpers)
    assert [(scope, kind) for _, scope, kind in calls] == [
        ("consumer", "draw helper call")
    ]
    assert not modules.exhausted


def test_lookups_cut_by_the_depth_limit_are_recorded():
    # lib passes along 12 re-exports, each read where it arrives. From the
    # consumer end, its lookup nests past a limit of 4 and is cut; from the
    # numpy end, kept results keep each lookup shallow. A cut is recorded, so
    # the package scan fails instead of depending on the order.
    sources = {"m0": "import numpy as lib\n"}
    sources |= {f"m{i}": f"from .m{i - 1} import lib\nlib\n" for i in range(1, 13)}
    sources["user"] = "from .m12 import lib\nlib.random.uniform()\n"
    consumer_first = list(reversed(sources))
    for order, max_depth, cut in [
        (consumer_first, 4, True),
        (list(sources), 4, False),
        (consumer_first, MAX_RESOLUTION_DEPTH, False),
    ]:
        modules = Modules(
            {
                f"pkg.{name}": ("pkg", lambda source=source: source)
                for name, source in sources.items()
            },
            max_depth=max_depth,
        )
        analyses = {
            name: analyse(sources[name], f"{name}.py", f"pkg.{name}", "pkg", modules)
            for name in order
        }
        assert bool(modules.exhausted) == cut
        if not cut:
            kinds = [kind for _, _, kind in analyses["user"].findings]
            assert kinds == ["random source"]


@pytest.mark.parametrize(
    "api",
    [
        "import numpy as lib\nleft, right = lib, 1\n",
        "import numpy as _lib\n__all__ = ['left'] + []\nleft = _lib\n",
        "import numpy as _lib\n__all__ = []\n__all__.append('left')\nleft = _lib\n",
        "import numpy as _lib\n__all__ = ('x',)\n__all__ += ['left']\nleft = _lib\n",
        "import numpy as _lib\n__all__ = names()\nleft = _lib\n",
    ],
)
def test_star_imports_bind_what_the_module_exports(api):
    user = "from .api import *\nleft.random.uniform()\n"
    assert _package_kinds({"api": api, "user": user}) == ["random source"]


def test_star_imports_bind_private_names_only_through_all():
    user = "from .api import *\n_lib.random.uniform()\n"
    assert _package_kinds({"api": "import numpy as _lib\n", "user": user}) == []
    api = "import numpy as _lib\n__all__ = ['_lib']\n"
    assert _package_kinds({"api": api, "user": user}) == ["random source"]


def test_cyclic_star_imports_resolve_in_any_order():
    sources = {
        "a": "from .b import *\nimport numpy as lib\n",
        "b": "from .a import *\n",
        "user": "from .b import *\nlib.random.uniform()\n",
    }
    results = [
        _package_findings(sources, order)
        for order in (["a", "b", "user"], ["user", "b", "a"], ["b", "user", "a"])
    ]
    assert results[0] == results[1] == results[2]
    assert [kind for _, _, kind in results[0]["user"]] == ["random source"]


@pytest.mark.parametrize(
    "sources",
    [
        {
            "a": "if flag:\n    import numpy as lib\nelse:\n    from .b import lib\n",
            "b": "from .a import lib\n",
            "other": "from .a import lib\nlib.random.uniform()\n",
            "user": "from .b import lib\nlib.random.uniform()\n",
        },
        # From via_a, a.lib leads to b.lib, then a.lib again, then b.lib,
        # which is cut: so that inner a.lib has none of b's numpy. Keeping
        # that partial answer would hide numpy from via_c, which reaches it
        # only through a.lib, whenever via_a is analysed first.
        {
            "a": "from .b import lib\n",
            "b": "if flag:\n    from .a import lib\nelse:\n    import numpy as lib\n",
            "c": "from .a import lib\n",
            "via_a": "from .a import lib\nlib.random.uniform()\n",
            "via_c": "from .c import lib\nlib.random.uniform()\n",
        },
    ],
)
def test_cyclic_named_imports_resolve_in_any_order(sources):
    results = [
        _package_findings(sources, list(order)) for order in permutations(sources)
    ]
    assert all(result == results[0] for result in results)
    for module, source in sources.items():
        if "lib.random" in source:
            assert [kind for _, _, kind in results[0][module]] == ["random source"]


def test_model_api_passes_on_cores_numpy_and_its_own_helpers():
    modules = package_scan().modules
    assert "numpy" in modules.star_binds("policyengine_us.model_api", "np")
    for api in ("policyengine_us.model_api", "policyengine_core.model_api"):
        assert "numpy.random.uniform" in modules.expand(f"{api}.np.random.uniform")
    assert "policyengine_us.model_api.all_of_variables" in modules.star_binds(
        "policyengine_us.model_api", "all_of_variables"
    )


def test_transitional_start_month_hash_is_a_draw_helper():
    module = (
        "policyengine_us.variables.gov.usda.snap.eligibility.work_requirements."
        "is_receiving_unemployment_compensation"
    )
    helpers = package_scan().helpers
    assert f"{module}.legacy_start_month_index" in helpers
    assert f"{module}.stored_start_month_index" in helpers
    assert f"{module}.situation_start_month_index" not in helpers
    assert f"{module}.start_month_supplied" not in helpers
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


def test_package_lookups_stay_within_the_depth_limit():
    exhausted = package_scan().modules.exhausted
    assert not exhausted, (
        f"{len(exhausted)} name lookups nested deeper than MAX_RESOLUTION_DEPTH "
        "and were cut, so what they found may depend on the order modules "
        "were scanned in. Raise the limit. One cut: " + repr(next(iter(exhausted)))
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
        "import importlib\n"
        "importlib.import_module(name='policyengine_us.tools.taxsim')\n",
        "import importlib\nimportlib.import_module('.taxsim', 'policyengine_us.tools')\n",
        "__import__('policyengine_us.tools', fromlist=['taxsim'])\n",
        "__import__('taxsim', globals(), locals(), [], 1)\n",
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
