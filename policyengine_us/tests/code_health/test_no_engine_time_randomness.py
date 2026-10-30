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
wherever in its body; either sends the name there in the code nested in
its scope too, unless that code binds the name itself), functions, lambdas
and comprehensions. An attribute
of a package module, or of a module EXTERNAL_EXPORTS maps, is what that
module binds under the name, so ``api.np.random`` is numpy's random module
where ``api`` is ``policyengine_core.model_api``. No code sees the names a
class body it is nested in binds, or its ``global`` and ``nonlocal``
statements. A module or class body looks further out
when no binding is sure to have run before the use with no ``del`` or
``except ... as`` cleanup that may come between (all are in an ``if``, loop,
``try``, ``with``, ``match`` or ``assert``, in a comprehension, past the
first operand of ``and``, ``or`` or a chained comparison, or in a branch of
a conditional expression, or the use comes first). A class body that binds
the name anywhere (an annotation alone or a ``del`` counts) then looks in
the module, never in a function around it, and so does what the body
evaluates: its annotations, its methods' defaults and annotations, and
type-parameter bounds and ``type`` values in it. A function may run
as soon as its ``def`` has run, so the scopes around it count only the
bindings before the ``def``, and every later deletion. A function's ``del``
of a name it declares ``global`` runs whenever the function is called, so
after the ``def`` it may come between any binding and any use. A generator
expression runs its body as it is iterated, so the same holds for it from
the expression (its first iterable runs at once). A class body,
a decorated function and a lambda may run before the statement that creates
them has bound its names (a decorator may call the function, and an
assignment's value may call a lambda in it), so code inside them doesn't
take those bindings as sure. Nor does a use take as sure a binding its own
statement makes (a multi-line assignment, or a default or base on a later
line of its ``def`` or ``class``): Python makes those after evaluating it,
and treating a walrus earlier in the statement the same way errs toward
reporting. An annotation is read as code that may run any time after its
statement starts, seeing a class body around it, which covers both ways
Python may evaluate it: with its statement, as up to 3.13, and whenever the
annotations are read, as 3.14 defers them (PEP 649). A type parameter's
bound or default and a ``type`` alias's value, which Python evaluates when
they are read (PEP 695, 3.12+; defaults PEP 696, 3.13+), are read the same
way. A ``type`` statement
binds its alias's name, but a type parameter's own name is not taken as
bound, which errs toward reporting. An annotation alone binds no value in a
module or class body.

So ``from numpy import random as r`` followed by ``r.random(3)`` is caught,
as are ``xp = np`` followed by ``xp.random.uniform()``, ``from
policyengine_us.model_api import np as lib`` followed by
``lib.random.uniform()``, and a ``try: import numpy as lib`` with a
fallback, while a local variable called ``random`` is not. A star import of
a package module binds its ``__all__`` (built from string literals with
``=``, ``+``, ``+=``, ``append``, ``extend``, ``insert`` or ``remove``; any
other ``__all__`` exports every name) or, without one, every name it binds
without a leading underscore. It may not bind a name an earlier or removed
``__all__`` held (an import cycle can see that one), one the module binds
only conditionally or deletes, or any name where ``__all__`` is built
otherwise, so the scan also looks further out. Where the module, while it
runs, may import the importing one (directly or through other modules,
counting every import in them, even in a function; the submodules a star
import of a package loads: the module each name its ``__all__`` lists
names below the package (``sub.leaf`` too, with ``sub``) or, where
``__all__`` is built otherwise, every module below it, and the same where
a literal ``__import__`` ``fromlist`` holds ``*`` (read as Python iterates
it: a list's, tuple's or set's elements, a dict's keys or a string's
characters, a literal ``*`` or ``**`` entry's own in its place); any call
whose literal arguments name a module as ``importlib.import_module`` or
``__import__`` would read them, whatever name the call is made under, a
relative one against its literal ``package`` (or the module's
``__package__`` or ``__name__``) or the package its ``globals`` give, as
Python reads them (``globals()`` or a dict literal, a literal ``**``
entry's own entries in its place and the last of a repeated key counting:
``__package__``, else ``__spec__``, else ``__name__`` and ``__path__``);
the packages an import starts; the code of modules it may
reach without importing them, as another module may have loaded them: an
attribute chain, ``getattr`` with a literal name, ``sys.modules`` with a
literal key, or the module a literal dynamic import returns, from a name
any import, or assignment (or walrus) of such a chain or a conditional
choice of one (``if``-``else``, ``and``, ``or``), in the module binds, a
submodule a star import of a package may bind, or in a package's
``__init__`` its own submodule; and the imports in code that may run
later, when it is called or read (functions, lambdas, generator
expressions, annotations, type parameters and ``type`` values), in the
packages around a module, which have run before it, and in the modules
they import or reach as they run, since its code may call that code), the
star import may see it part-run, before it binds a name or sets ``__all__``: it may then bind any
name the module binds without a leading underscore, and binds none surely.
EXTERNAL_EXPORTS lists the
names numpy and ``policyengine_core.model_api`` bind where they matter here;
``np``, ``numpy`` and ``pd`` are bound to numpy and pandas wherever nothing
else binds them. Reported, as (file, enclosing function or class, kind):
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
of a computed name (a relative dynamic import whose ``package`` or
``globals`` is computed is read against the module's own package),
package search paths changed as the code runs (a ``__path__`` assignment)
or import hooks, code outside the package (what it imports, or calls back
into), values reached through objects or containers (``self.r =
np.random`` is caught where ``np.random`` is read; a later
``self.r.uniform()`` is not; nor are functions one module sets on another
or registers for a later call), names bound otherwise than by an import or
an assignment to a plain name (unpacking, ``for``, ``with``, parameters),
the values calls return (``r =
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
import sys
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
    # SHA-256 content check of a stored dataset, in a scoring preflight run
    # before a Social Security reform is scored.
    "tools/social_security_preflight.py": {
        ("<module>", "hash library"): 1,
        ("_file_sha256", "hash use"): 1,
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
TYPE_ALIAS = getattr(ast, "TypeAlias", ())  # Python 3.12+
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
    """One namespace: a module, class, function, lambda or comprehension, or
    the annotations of one statement."""

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
        # (line, module, conditional, importing module) for each star
        # import.
        self.stars = []
        # Names a global or nonlocal statement gives to another scope.
        self.declared = {}
        # For a function, lambda or class body, the names Python makes
        # local to it.
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
        for star_line, base, conditional, importer in self.stars:
            provided = self.modules.star_binds(base, name, importer)
            if provided is not None:
                targets |= provided
                sure = self.modules.star_binds_surely(base, name, importer)
                entries.append((star_line, conditional or not sure))
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

    def resolve(self, name, line=None, deferred=False, statement=None) -> set:
        """Every dotted target ``name`` may refer to at ``line``.

        The answer errs toward reporting: the targets of every binding that
        may be the one read, in each scope Python looks in until a binding is
        sure to hold. ``deferred`` says the code may run at any time after
        ``line``. ``statement`` is the (first line, last line) of the
        statement the use is in, whose own bindings may not have happened.
        """
        targets = set()
        # The scope a global or nonlocal statement sends the name to, until
        # the lookup reaches it.
        owner = None
        first = True
        unfinished = [statement] if statement else []
        scope = self
        while scope is not None:
            if scope.kind == "annotation":
                # Up to 3.13 an annotation is evaluated with its statement.
                # 3.14 defers it to whenever the annotations are read (PEP
                # 649), any time after the statement starts, in a scope that
                # also sees a class body around it. Reading it as deferred
                # from the statement covers both, since no binding the
                # statement makes is sure (resolve).
                line, deferred = scope.line, True
                scope = scope.parent
                continue
            if scope is owner:
                owner = None
            # A global or nonlocal name skips the scopes up to the one it
            # names, and no code nested in a class body sees the names it
            # binds or declares.
            if owner is None and (first or scope.kind != "class"):
                # A global or nonlocal statement here sends the name there,
                # here and in the code nested here.
                owner = scope.declared.get(name)
                if owner is None:
                    found, bound, falls = scope.own(name, line, deferred, unfinished)
                    targets |= found
                    if bound and not falls:
                        return targets
                    if scope.kind == "class" and name in scope.local_names:
                        # A class body that binds the name reads it from its
                        # namespace, then the module's (LOAD_NAME): the
                        # functions around it are skipped.
                        owner = scope
                        while owner.parent is not None:
                            owner = owner.parent
            if scope.unfinished is not None:
                # It may run before its statement's bindings have happened.
                unfinished.append(scope.unfinished)
            if scope.kind in ("function", "lambda", "generator"):
                # A function may run as soon as its def has run, and a
                # generator expression's body as soon as it is made, so the
                # scopes around them are read as of then, and any later
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
    body = node.body if isinstance(node.body, list) else [node.body]
    return frozenset(names) | _block_locals(body)


def _block_locals(body) -> frozenset:
    """The names Python makes local to a block of statements, wherever it
    binds them: every name bound outside nested scopes, an annotation alone
    and a ``del`` included, less those a global or nonlocal statement sends
    elsewhere."""
    names, declared = set(), set()
    stack = list(body)
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


def _may_not_run(node, child) -> bool:
    """Whether ``child``, a part of ``node``, may not run when ``node`` does:
    an operand of ``and`` or ``or`` after the first, a chained comparison's
    after the second, a conditional expression's branches, and all of an
    ``assert``, which ``python -O`` drops."""
    if isinstance(node, ast.BoolOp):
        return child is not node.values[0]
    if isinstance(node, ast.Compare):
        return any(child is part for part in node.comparators[1:])
    if isinstance(node, ast.IfExp):
        return child is not node.test
    return isinstance(node, ast.Assert)


def _type_parameter_values(node) -> list:
    """The bounds and defaults of a definition's type parameters (PEP 695,
    Python 3.12+; defaults 3.13+), which Python evaluates when they are
    read."""
    values = []
    for parameter in getattr(node, "type_params", []):
        for field in ("bound", "default_value"):
            value = getattr(parameter, field, None)
            if value is not None:
                values.append(value)
    return values


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


class _Exports(NamedTuple):
    # Names __all__ holds once the module has run.
    final: frozenset
    # Names it held before, or that were removed, which a module importing it
    # during an import cycle may see.
    earlier: frozenset


def _public_names(tree):
    """What ``from module import *`` binds, from the module's ``__all__``.

    An _Exports, DEFAULT_PUBLIC without an ``__all__``, or EVERY_NAME for an
    ``__all__`` built other than from string literals with ``=``, ``+``,
    ``+=``, ``append``, ``extend``, ``insert`` and ``remove`` at the top
    level.
    """
    uses = {node for node in ast.walk(tree) if _is_all(node)}
    if not uses:
        return DEFAULT_PUBLIC
    names, seen, handled = set(), set(), set()
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
                removed = _literal(args[0]) if len(args) == 1 else None
                # Without a literal, any name may be the one removed.
                names = names - {removed} if removed else set()
                value = set()
            if value is None:
                return EVERY_NAME
            names = names | value
        if value is not None:
            handled |= {node for node in ast.walk(statement) if _is_all(node)}
            seen |= names
    if uses - handled:
        return EVERY_NAME
    return _Exports(frozenset(names), frozenset(seen - names))


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
        # module -> the package modules it may start, or whose code it may
        # reach, when it runs.
        self.imported = {}
        # module -> the modules it star-imports from.
        self.star_bases = {}
        # module -> (the package modules it imports or reaches as it runs,
        # the packages it star-imports from as it runs).
        self.run_imports = {}
        # module -> (the package modules code in it that may run later
        # imports or reaches, the packages that code star-imports from).
        self.later_imports = {}
        # package -> the modules below it; every module and package around one.
        self._below = None
        self._known = None
        self._reached = {}
        # the packages around a module -> (the package modules that ran
        # before it, the package modules their later code may start).
        self._ran = {}
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
            package = self._package(module)
            (run, run_stars), (later, later_stars) = _imports_in(tree, package, module)
            self._index()
            run_reached, later_reached = _references_in(
                tree, package, run_stars | later_stars, self._known, module
            )
            run, later = run | run_reached, later | later_reached
            # Its code may call a function that imports, so every import
            # counts.
            self.imported[module] = self._imports_of(module, run | later)
            self.star_bases[module] = frozenset(run_stars | later_stars)
            self.run_imports[module] = (
                self._imports_of(module, run),
                frozenset(run_stars),
            )
            self.later_imports[module] = (
                self._imports_of(module, later),
                frozenset(later_stars),
            )

    def _package(self, module):
        return self.sources.get(module, (None,))[0]

    def _imports_of(self, module, names) -> frozenset:
        """The package modules ``module`` may start, or reach, through
        ``names`` (from ``_imports_in`` and ``_references_in``): each one and
        the packages around it. The packages around ``module`` have started
        before it. Star imports' submodules are added by ``reached``."""
        started = _started(module)
        imported = set()
        for name in names:
            parts = name.split(".")
            for end in range(1, len(parts) + 1):
                prefix = ".".join(parts[:end])
                if prefix in self.sources and prefix not in started:
                    imported.add(prefix)
        return frozenset(imported)

    def reached(self, module) -> frozenset:
        """The package modules ``module`` may start while it runs, directly
        or through those it starts."""
        if module not in self._reached:
            seen, stack = set(), [module]
            while stack:
                current = stack.pop()
                self.top(current)
                fresh = (
                    self.imported[current]
                    | self.star_loads(current)
                    | self.called(current)
                ) - seen
                seen |= fresh
                stack.extend(fresh)
            self._reached[module] = frozenset(seen)
        return self._reached[module]

    def called(self, module) -> frozenset:
        """The package modules ``module``'s code may start by calling or
        reading code that may run later in the modules that ran before it:
        the packages around it, and the package modules their code, as it
        ran, imported, directly or through the modules it started."""
        around = _started(module) - {module}
        if around not in self._ran:
            ran = {package for package in around if package in self.sources}
            stack = list(ran)
            while stack:
                current = stack.pop()
                self.top(current)
                names, bases = self.run_imports[current]
                fresh = (names | self._star_children(bases)) - ran
                ran |= fresh
                stack.extend(fresh)
            starts = set()
            for current in ran:
                names, bases = self.later_imports[current]
                starts |= names | self._star_children(bases)
            self._ran[around] = (frozenset(ran), frozenset(starts))
        return self._ran[around][1] - _started(module)

    def star_loads(self, module) -> frozenset:
        """The modules ``module``'s star imports of packages may start below
        them: what each name a package's ``__all__`` lists, in any version
        of it, names below the package, with the packages on the way
        (Python imports the package's name, a dot and the listed name,
        dotted or not), or every module below it where ``__all__`` is built
        otherwise. A star import of a package without ``__all__`` starts
        none. The packages around ``module`` have started before it."""
        return self._star_children(self.star_bases[module]) - _started(module)

    def _index(self):
        if self._below is None:
            self._below, known = {}, set()
            for name in self.sources:
                known |= _started(name)
                parts = name.split(".")
                for end in range(1, len(parts)):
                    self._below.setdefault(".".join(parts[:end]), set()).add(name)
            self._known = frozenset(known)

    def _star_children(self, bases) -> frozenset:
        """The modules below them star imports from ``bases`` may start."""
        self._index()
        loads = set()
        for base in bases:
            if base not in self.sources:
                continue
            self.top(base)
            public = self.publics[base]
            if public == EVERY_NAME:
                loads |= self._below.get(base, set())
            elif isinstance(public, _Exports):
                for listed in public.final | public.earlier:
                    parts = f"{base}.{listed}".split(".")
                    for end in range(base.count(".") + 2, len(parts) + 1):
                        path = ".".join(parts[:end])
                        if path in self.sources:
                            loads.add(path)
        return frozenset(loads)

    def cyclic(self, importer, base) -> bool:
        """Whether ``importer``'s star import of ``base`` may run while
        ``base`` is still running, and see only what it has bound so far:
        when ``base`` may start ``importer``, or is it."""
        return importer == base or importer in self.reached(base)

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
        """(bound, targets, falls through) for ``module``'s top-level
        ``name`` once it ran: whether any statement binds it, what to, and
        whether it may be unbound after all."""

        def compute():
            targets, bound, falls = self.top(module).own(name, None, True)
            return bound, frozenset(targets), falls

        cut = (False, frozenset(), True)
        return self.guarded(("binding", module, name), cut, compute)

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

    def star_binds(self, base, name, importer):
        """What ``from base import *`` in ``importer`` binds ``name`` to, or
        None."""
        if base not in self.sources:
            mapped = self.external.get(base, {}).get(name)
            return {mapped} if mapped else None
        self.top(base)
        public = self.publics[base]
        if public == DEFAULT_PUBLIC:
            exported = not name.startswith("_")
        elif public == EVERY_NAME:
            exported = True
        else:
            exported = name in public.final or name in public.earlier
            if not exported and not name.startswith("_"):
                # In an import cycle it may run before base sets __all__,
                # and then binds every public name base has bound.
                exported = self.cyclic(importer, base) and self.binding(base, name)[0]
        if not exported:
            return None
        bound, targets, _ = self.binding(base, name)
        if bound:
            return set(targets)
        if isinstance(public, _Exports):
            return {f"{base}.{name}"}  # A submodule __all__ lists.
        return None

    def star_binds_surely(self, base, name, importer) -> bool:
        """Whether ``from base import *`` in ``importer``, which star_binds
        says may bind ``name``, is sure to."""
        if base not in self.sources:
            return True
        if self.cyclic(importer, base):
            return False  # It may run before base binds anything.
        public = self.publics[base]
        if public == EVERY_NAME:
            return False
        if isinstance(public, _Exports) and name not in public.final:
            return False  # Only an earlier or removed __all__ held it.
        bound, _, falls = self.binding(base, name)
        return not (bound and falls)


def _build_scopes(tree, module, package, modules):
    """(module scope, the innermost scope of every node, the (first line,
    last line) of the innermost statement around every node) of ``tree``."""
    top = _Scope("module", "<module>", None, modules)
    scope_of, statement_of = {}, {}

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

    def visit_annotations(annotations, scope, line, conditional):
        # Evaluated in the outer scope, with the statement or later (see
        # _Scope.resolve); the statement's own bindings are not sure for
        # them, as for any use in it.
        if not annotations:
            return
        inner = _Scope("annotation", scope.qualname, scope, modules, line)
        for annotation in annotations:
            visit(annotation, inner, conditional)

    def visit_function(node, scope, conditional):
        # Decorators and defaults are evaluated in the outer scope.
        outer = list(getattr(node, "decorator_list", []))
        outer += node.args.defaults + [d for d in node.args.kw_defaults if d]
        for child in outer:
            visit(child, scope, conditional)
        if not isinstance(node, ast.Lambda):
            annotations = [node.returns] if node.returns else []
            annotations += [
                argument.annotation
                for argument in ast.walk(node.args)
                if isinstance(argument, ast.arg) and argument.annotation
            ]
            annotations += _type_parameter_values(node)
            visit_annotations(annotations, scope, node.lineno, conditional)
        name = getattr(node, "name", "<lambda>")
        if not isinstance(node, ast.Lambda):
            top_level = scope.parent is None
            target = f"{module}.{name}" if top_level else None
            scope.bind(name, node.lineno, target, conditional)
        qualname = name if scope.parent is None else f"{scope.qualname}.{name}"
        kind = "lambda" if isinstance(node, ast.Lambda) else "function"
        inner = _Scope(kind, qualname, scope, modules, node.lineno)
        if getattr(node, "decorator_list", None):
            # A decorator may call the function before its name is bound. A
            # lambda's body is part of its own statement, which every use
            # in it already treats as unfinished (resolve).
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
        visit_annotations(_type_parameter_values(node), scope, node.lineno, conditional)
        top_level = scope.parent is None
        target = f"{module}.{node.name}" if top_level else None
        scope.bind(node.name, node.lineno, target, conditional)
        qualname = node.name if top_level else f"{scope.qualname}.{node.name}"
        inner = _Scope("class", qualname, scope, modules, node.lineno)
        inner.unfinished = statement_span[-1]
        inner.local_names = _block_locals(node.body)
        declare(inner, node.body)
        for child in node.body:
            visit(child, inner)

    def visit_comprehension(node, scope, conditional):
        # The first iterable is evaluated in the enclosing scope; the rest
        # in the comprehension's own, reported under the enclosing name.
        visit(node.generators[0].iter, scope, conditional)
        # A generator expression runs the rest when it is iterated.
        kind = "generator" if isinstance(node, ast.GeneratorExp) else "comprehension"
        inner = _Scope(kind, scope.qualname, scope, modules, node.lineno)
        # The rest may run any number of times, a generator expression's
        # only as it is iterated, so a walrus in it may not bind.
        for index, generator in enumerate(node.generators):
            scope_of[generator] = inner
            if index:
                visit(generator.iter, inner, True)
            assign(generator.target, None, inner, False)
            for condition in generator.ifs:
                visit(condition, inner, True)
        if isinstance(node, ast.DictComp):
            elements = [node.key, node.value]
        else:
            elements = [node.elt]
        for element in elements:
            visit(element, inner, True)

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
        statement_of[node] = statement_span[-1]
        if isinstance(node, FUNCTION_NODES + (ast.Lambda,)):
            return visit_function(node, scope, conditional)
        if isinstance(node, ast.ClassDef):
            return visit_class(node, scope, conditional)
        if isinstance(node, COMPREHENSION_NODES):
            return visit_comprehension(node, scope, conditional)
        if isinstance(node, TYPE_ALIAS):
            # Its value is evaluated when it is read, like an annotation.
            scope_of[node.name] = scope
            scope.bind(node.name.id, node.lineno, None, conditional)
            values = [node.value] + _type_parameter_values(node)
            return visit_annotations(values, scope, node.lineno, conditional)
        if isinstance(node, ast.Assign):
            visit(node.value, scope, conditional)
            for target in node.targets:
                assign(target, node.value, scope, conditional)
            return
        if isinstance(node, ast.AnnAssign):
            body = scope.kind in ("module", "class")
            if body and node.simple:
                visit_annotations([node.annotation], scope, node.lineno, conditional)
            else:
                # 3.14 never evaluates this one; earlier versions do, with
                # the statement, outside a function.
                visit(node.annotation, scope, conditional)
            if node.value is not None:
                visit(node.value, scope, conditional)
            elif body and isinstance(node.target, ast.Name):
                # An annotation alone binds no value here; in a function it
                # still makes the name local.
                scope_of[node.target] = scope
                return
            return assign(node.target, node.value, scope, conditional)
        if isinstance(node, ast.NamedExpr):
            visit(node.value, scope, conditional)
            # The target belongs to the scope around any comprehensions or
            # annotations; the value is evaluated where the expression is.
            owner = scope
            while owner.kind in ("comprehension", "generator", "annotation"):
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
                    scope.stars.append((node.lineno, base, conditional, module))
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
            visit(child, scope, inside or _may_not_run(node, child))

    visit(tree, top)
    return top, scope_of, statement_of


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


def _anchor(node, module):
    """The package a literal, or the module's ``__name__``, names, else None
    (callers read anything computed, ``__package__`` or ``__spec__.parent``
    too, as the module's own package)."""
    if _literal(node) is not None:
        return _literal(node)
    if isinstance(node, ast.Name) and node.id == "__name__":
        return module
    return None


def _is_none(node) -> bool:
    return isinstance(node, ast.Constant) and node.value is None


def _dict_entries(node) -> list:
    """(key, value) for each entry of dict literal ``node``, in order, a
    literal ``**`` dict's own entries in its place; a computed ``**`` entry
    gives (None, the mapping)."""
    entries = []
    for key, value in zip(node.keys, node.values):
        if key is None and isinstance(value, ast.Dict):
            entries += _dict_entries(value)
        else:
            entries.append((key, value))
    return entries


def _iterated(node) -> list:
    """The items Python gets iterating ``node``, as far as it is literal: a
    string's characters, a list's, tuple's or set's elements and a dict's
    keys, a ``*`` or ``**`` entry's own in its place. An item that is not a
    literal string is None; a computed iterable gives none."""
    if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        items = []
        for element in node.elts:
            if isinstance(element, ast.Starred):
                items += _iterated(element.value)
            else:
                items.append(_literal(element))
        return items
    if isinstance(node, ast.Dict):
        return [_literal(key) for key, _ in _dict_entries(node)]
    return list(_literal(node) or "")


def _globals_package(node, package, module):
    """The package a relative ``__import__`` with ``globals`` ``node``
    imports from, as Python reads it: ``__package__``, else
    ``__spec__.parent``, else ``__name__``, the package around it unless
    ``__path__`` is set; None where it has neither, and Python raises.
    A dict literal's literal ``**`` entries are read in place; anything
    else (``globals()``, a computed mapping, or a dict literal with a
    computed key or ``**`` entry) is read as the module's own globals."""
    if not isinstance(node, ast.Dict):
        return package
    pairs = _dict_entries(node)
    if not all(isinstance(key, ast.Constant) for key, _ in pairs):
        return package
    # The last of a repeated key wins, as in the dict Python builds; a
    # None value then reads as absent. Keys that aren't strings are
    # never ones Python reads.
    entries = {key.value: value for key, value in pairs}
    given = {key: value for key, value in entries.items() if not _is_none(value)}
    if "__package__" in given:
        return _anchor(given["__package__"], module) or package
    if "__spec__" in given:
        return package
    if "__name__" not in given:
        return None
    name = _anchor(given["__name__"], module)
    if name is None:
        return package
    return name if "__path__" in entries else name.rpartition(".")[0]


def _dynamic_imports(call, called, package, module=None) -> list:
    """Absolute names a call of a dynamic import function imports, where its
    arguments are literals: ``base.*`` where an ``__import__`` ``fromlist``
    holds ``*``."""
    names = []
    if "importlib.import_module" in called:
        name = _literal(_argument(call, 0, "name"))
        given = _argument(call, 1, "package")
        relative_to = _anchor(given, module)
        if relative_to is None and given is not None and _literal(given) is None:
            # A computed package is read as the module's own; without one,
            # Python raises.
            relative_to = None if _is_none(given) else package
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
            relative_to = _globals_package(
                _argument(call, 1, "globals"), package, module
            )
            base = _absolute(name, level, relative_to) if level else name
            names.append(base)
            items = _iterated(_argument(call, 3, "fromlist"))
            names += [f"{base}.{item}" for item in items if item]
    return names


# Code that may run after the statement holding it, when it is called or
# read, so after the module has run: as may annotations (deferred from 3.14),
# type parameters and ``type`` values.
LATER_NODES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.GeneratorExp)
LATER_FIELDS = ("annotation", "type_params")


def _later_walk(tree):
    """(node, whether it may run later) for every node of ``tree``: in a
    function, lambda or generator expression (with its decorators, defaults
    and first iterable, which run at once, to be safe), an annotation, type
    parameters or a ``type`` alias."""
    stack = [(tree, False)]
    while stack:
        node, later = stack.pop()
        yield node, later
        later = later or isinstance(node, LATER_NODES) or isinstance(node, TYPE_ALIAS)
        for field, value in ast.iter_fields(node):
            for child in value if isinstance(value, list) else [value]:
                if isinstance(child, ast.AST):
                    stack.append((child, later or field in LATER_FIELDS))


def _imports_in(tree, package, module=None):
    """((names, star bases) of the imports that run with ``tree``'s module,
    (names, star bases) of those in code that may run later (``_later_walk``).

    Names are absolute, as an import, or a call whose literal arguments name
    a module as ``importlib.import_module`` or ``__import__`` would read
    them, imports them, whatever name the call is made under: an alias, a
    re-export or ``getattr`` may make it one. Star bases are the packages a
    star import, or ``__import__`` with ``*`` in its ``fromlist``, loads
    from."""
    found = {False: (set(), set()), True: (set(), set())}
    for node, later in _later_walk(tree):
        names, stars = found[later]
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            base = _absolute(node.module or "", node.level, package)
            names.add(base)
            names.update(f"{base}.{alias.name}" for alias in node.names)
            if any(alias.name == "*" for alias in node.names):
                stars.add(base)
        elif isinstance(node, ast.Call):
            for name in _dynamic_imports(node, DYNAMIC_IMPORTS, package, module):
                names.add(name)
                if name.endswith(".*"):
                    stars.add(name[: -len(".*")])
    return found[False], found[True]


# What _references_in's rules read, with the paths on the way.
REFERENCE_NAMES = frozenset(
    {"getattr", "builtins", "builtins.getattr", "sys", "sys.modules", "sys.modules.get"}
)


def _references_in(tree, package, stars, known, module=None):
    """(paths code that runs with ``tree``'s module may name, paths code that
    may run later may name; ``_later_walk``).

    Another module may have loaded a module, which is then an attribute of
    its package, so code can reach it, and call its functions, without
    importing it. Each name, attribute chain, ``getattr`` with a literal
    name, ``sys.modules`` read with a literal key (``[]`` or ``get``) and
    literal dynamic import (the module or its top package, which it
    returns), and each branch of a conditional expression, ``and`` or
    ``or``, names every path its first name may: what any import in the
    module, or assignment of such an expression (or walrus), binds the name
    to (an assignment may name the name itself, as in ``x = x.sub``), the name
    itself, the name below each package in ``stars`` (a star import of a
    package binds its loaded submodules), and in a package's ``__init__``
    the name below the package. Only paths in ``known`` (each package module
    and the packages around it), from which a module may yet be named, and
    those the rules read are kept. Which paths are package modules is the
    caller's to say."""
    bound = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.asname or alias.name.split(".")[0]
                bound.setdefault(name, []).append(alias.name if alias.asname else name)
        elif isinstance(node, ast.ImportFrom):
            base = _absolute(node.module or "", node.level, package)
            for alias in node.names:
                if alias.name != "*":
                    name = alias.asname or alias.name
                    bound.setdefault(name, []).append(f"{base}.{alias.name}")
        elif isinstance(node, (ast.Assign, ast.AnnAssign, ast.NamedExpr)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if isinstance(target, ast.Name) and node.value is not None:
                    bound.setdefault(target.id, []).append(node.value)
    around = list(stars) + ([package] if package and module in (None, package) else [])
    keep = known | REFERENCE_NAMES
    names = {}

    def name_paths(name):
        if name not in names:
            names[name] = ({name} | {f"{base}.{name}" for base in around}) & keep
        return names[name]

    def paths(node):
        return _paths(node) & keep

    def _paths(node):
        if isinstance(node, ast.Name):
            return name_paths(node.id)
        if isinstance(node, ast.Attribute):
            return {f"{path}.{node.attr}" for path in paths(node.value)}
        if isinstance(node, ast.Subscript):
            key = _literal(node.slice)
            if key and "sys.modules" in paths(node.value):
                return {key}
            return set()
        if isinstance(node, ast.IfExp):
            return paths(node.body) | paths(node.orelse)
        if isinstance(node, ast.BoolOp):
            return set().union(*map(paths, node.values))
        if isinstance(node, ast.NamedExpr):
            return paths(node.value)
        if not isinstance(node, ast.Call):
            return set()
        called = paths(node.func)
        if called & {"getattr", "builtins.getattr"} and len(node.args) >= 2:
            attribute = _literal(node.args[1])
            if attribute:
                return {f"{path}.{attribute}" for path in paths(node.args[0])}
        if "sys.modules.get" in called and node.args and _literal(node.args[0]):
            return {_literal(node.args[0])}
        returned = set()
        for name in _dynamic_imports(node, DYNAMIC_IMPORTS, package, module):
            if not name.endswith(".*"):
                returned |= {name, name.split(".")[0]}
        return returned

    # Bind each name to what its imports and assignments name, until no
    # path is new: kept paths are finite, so this ends.
    changed = True
    while changed:
        changed = False
        for name, values in bound.items():
            for value in values:
                fresh = ({value} & keep if isinstance(value, str) else paths(value)) - (
                    name_paths(name)
                )
                if fresh:
                    names[name] |= fresh
                    changed = True

    found = {False: set(), True: set()}
    for node, later in _later_walk(tree):
        if isinstance(node, (ast.Name, ast.Attribute, ast.Subscript, ast.Call)):
            found[later] |= paths(node)
    return found[False], found[True]


def _started(module) -> frozenset:
    """``module`` and the packages around it, which start before it runs."""
    parts = module.split(".")
    return frozenset(".".join(parts[:end]) for end in range(1, len(parts) + 1))


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
    top, scope_of, statement_of = _build_scopes(tree, module, package, modules)
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

    def statement_for(node):
        while node not in statement_of:
            node = parents[node]
        return statement_of[node]

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
            for target in scope_for(node).resolve(
                root, node.lineno, statement=statement_for(node)
            )
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
                for name in _dynamic_imports(node, called, package, module):
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
        # 3.14 evaluates annotations when they are read (PEP 649), after any
        # later deletion; up to 3.13 they run with their statement.
        ("hash = str\ndef f(x: hash('x')):\n    pass\ndel hash\n", "builtin hash"),
        ("hash = str\ndef f() -> hash('x'):\n    pass\ndel hash\n", "builtin hash"),
        (
            "class C:\n"
            "    hash = str\n"
            "    def f(self, x: hash('x')):\n"
            "        pass\n"
            "    del hash\n",
            "builtin hash",
        ),
        (
            "class C:\n    hash = str\n    y: hash('x') = 1\n    del hash\n",
            "builtin hash",
        ),
        ("hash = str\ny: hash('x') = 1\ndel hash\n", "builtin hash"),
        ("def hash(x: hash('x')):\n    pass\n", "builtin hash"),
        # A statement binds its names only after evaluating them.
        ("hash = (\n    hash('x')\n)\n", "builtin hash"),
        ("def hash(\n    value=hash('x'),\n):\n    return value\n", "builtin hash"),
        ("class hash(\n    make(hash('x')),\n):\n    pass\n", "builtin hash"),
        ("(\n    hash\n) = (\n    hash('x')\n)\n", "builtin hash"),
        # An annotation alone binds no value in a module or class body.
        ("hash: int\nkey = hash('x')\n", "builtin hash"),
        (
            "import numpy as lib\nclass C:\n    lib: object\n    answer = lib.random.uniform()\n",
            "random source",
        ),
        # A function may run before a later binding, or after a deletion.
        (
            "def consumer(value):\n"
            "    return hash(value)\n"
            "answer = consumer('x')\n"
            "hash = str\n",
            "builtin hash",
        ),
        ("hash = str\ndef f(x):\n    return hash(x)\ndel hash\n", "builtin hash"),
        # A walrus in a generator expression binds around it.
        (
            "import numpy as np\nlist((lib := np) for _ in 'x')\nlib.random.uniform()\n",
            "random source",
        ),
        ("import importlib\nimportlib.import_module('random')\n", "stochastic import"),
        (
            "import importlib\nimportlib.import_module(name='random')\n",
            "stochastic import",
        ),
        ("__import__('numpy.random')\n", "stochastic import"),
        ("__import__('numpy', fromlist=['random'])\n", "stochastic import"),
        # Python iterates a fromlist, unpacked entries too.
        ("__import__('numpy', fromlist={**{'random': None}})\n", "stochastic import"),
        ("__import__('numpy', fromlist=[*('random',)])\n", "stochastic import"),
        ("__import__('numpy', fromlist={*'x', *{'random': 0}})\n", "stochastic import"),
        # At any depth.
        (
            "__import__('numpy', fromlist={**{**{'random': None}}})\n",
            "stochastic import",
        ),
        ("__import__('numpy', fromlist=[*[*('random',)]])\n", "stochastic import"),
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
        # An annotation reads a binding sure to have run before its
        # statement; a deferred one in a class body also sees the class.
        "hash = str\ndef f(x: hash('x')):\n    pass\n",
        "class C:\n    hash = str\n    def f(self, x: hash('x')):\n        pass\n",
        "hash = str\ny: hash('x') = 1\n",
        # A statement's bindings count for the statements after it.
        "hash = str\nkey = (\n    hash('x')\n)\n",
        "class A:\n    hash = str\n    key = (\n        hash('x')\n    )\n",
        "def hash(x):\n    return (\n        hash(x - 1)\n    ) if x else 0\nhash(1)\n",
        # An annotated value binds; in a function an annotation alone makes
        # the name local (UnboundLocalError), hiding the builtin.
        "hash: object = str\nkey = hash('x')\n",
        "def f():\n    hash: object\n    return hash('x')\n",
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


# Python runs these when they are used, not where they are written, so a
# later deletion of a shadowing global counts; a list comprehension runs at
# once. Each needs the syntax of the Python 3 minor version given.
@pytest.mark.parametrize(
    "source, reaches_builtin, minor",
    [
        ("hash = str\ng = (hash(v) for v in 'x')\ndel hash\nlist(g)\n", True, 11),
        ("hash = str\ng = (hash(v) for v in 'x')\nlist(g)\n", False, 11),
        ("hash = str\nkeys = [hash(v) for v in 'x']\ndel hash\n", False, 11),
        ("hash = str\ntype X = hash('x')\ndel hash\nX.__value__\n", True, 12),
        ("hash = str\ntype X = hash('x')\nX.__value__\n", False, 12),
        (
            "hash = str\n"
            "type X[T: hash('x')] = list[T]\n"
            "del hash\n"
            "X.__type_params__[0].__bound__\n",
            True,
            12,
        ),
        (
            "hash = str\n"
            "def f[T: hash('x')]():\n"
            "    pass\n"
            "del hash\n"
            "f.__type_params__[0].__bound__\n",
            True,
            12,
        ),
        (
            "hash = str\n"
            "class C[T: hash('x')]:\n"
            "    pass\n"
            "del hash\n"
            "C.__type_params__[0].__bound__\n",
            True,
            12,
        ),
        (
            "class C:\n"
            "    hash = str\n"
            "    def m[T: hash('x')](self):\n"
            "        pass\n"
            "    del hash\n"
            "C.m.__type_params__[0].__bound__\n",
            True,
            12,
        ),
        (
            "hash = str\n"
            "def f[T = hash('x')]():\n"
            "    pass\n"
            "del hash\n"
            "f.__type_params__[0].__default__\n",
            True,
            13,
        ),
    ],
)
def test_code_python_runs_when_used_sees_later_deletions(
    source, reaches_builtin, minor
):
    if sys.version_info < (3, minor):
        pytest.skip(f"needs Python 3.{minor} syntax")
    expected = {"builtin hash"} if reaches_builtin else set()
    assert {kind for _, _, kind in draw_findings(source)} == expected


# Each is the body of a function outer that binds hash = str. A class body
# that binds hash anywhere, even by an annotation alone, a del, or a later,
# conditional or failed binding, reads it from its own namespace, then the
# module's, so here the builtin; so does what the body evaluates, its
# methods' defaults and annotations and its first comprehension iterables
# included. Code nested in the class reads outer's. Each needs the syntax of
# the Python 3 minor version given.
@pytest.mark.parametrize(
    "body, reaches_builtin, minor",
    [
        ("    class C:\n        key = hash('x')\n        hash = int\n", True, 11),
        ("    class C:\n        hash: int\n        key = hash('x')\n", True, 11),
        (
            "    class C:\n"
            "        if False:\n"
            "            hash = int\n"
            "        key = hash('x')\n",
            True,
            11,
        ),
        (
            "    class C:\n"
            "        hash = int\n"
            "        del hash\n"
            "        key = hash('x')\n",
            True,
            11,
        ),
        (
            "    class C:\n"
            "        try:\n"
            "            raise ValueError\n"
            "        except ValueError as hash:\n"
            "            pass\n"
            "        key = hash('x')\n",
            True,
            11,
        ),
        (
            "    class C:\n"
            "        try:\n"
            "            del hash\n"
            "        except NameError:\n"
            "            pass\n"
            "        key = hash('x')\n",
            True,
            11,
        ),
        (
            "    class C:\n"
            "        try:\n"
            "            from no_such_module_anywhere import hash\n"
            "        except ImportError:\n"
            "            pass\n"
            "        key = hash('x')\n",
            True,
            11,
        ),
        (
            "    class C:\n"
            "        hash: int\n"
            "        y: hash('x')\n"
            "    C.__annotations__\n",
            True,
            11,
        ),
        (
            "    class C:\n"
            "        hash: int\n"
            "        def m(self, x: hash('x')):\n"
            "            pass\n"
            "    C.m.__annotations__\n",
            True,
            11,
        ),
        (
            "    class C:\n"
            "        hash: int\n"
            "        def m(self, x=hash('x')):\n"
            "            pass\n",
            True,
            11,
        ),
        (
            "    class C:\n"
            "        hash: int\n"
            "        keys = [v for v in [hash('x')]]\n",
            True,
            11,
        ),
        (
            "    class C:\n"
            "        hash: int\n"
            "        def m[T: hash('x')](self):\n"
            "            pass\n"
            "    C.m.__type_params__[0].__bound__\n",
            True,
            12,
        ),
        (
            "    class C:\n"
            "        hash: int\n"
            "        type X = hash('x')\n"
            "    C.X.__value__\n",
            True,
            12,
        ),
        # Past a nonlocal statement around the class.
        (
            "    def middle():\n"
            "        nonlocal hash\n"
            "        class C:\n"
            "            hash: int\n"
            "            key = hash('x')\n"
            "    middle()\n",
            True,
            11,
        ),
        # The class binds hash first, or not at all, or the read is in code
        # nested in the class: outer's str.
        ("    class C:\n        hash = str\n        key = hash('x')\n", False, 11),
        ("    class C:\n        key = hash('x')\n", False, 11),
        (
            "    class C:\n"
            "        hash: int\n"
            "        def m(self):\n"
            "            return hash('x')\n"
            "    C().m()\n",
            False,
            11,
        ),
        (
            "    class C:\n        hash: int\n        keys = [hash(v) for v in 'x']\n",
            False,
            11,
        ),
    ],
)
def test_a_class_body_that_binds_a_name_reads_it_from_the_module(
    body, reaches_builtin, minor
):
    if sys.version_info < (3, minor):
        pytest.skip(f"needs Python 3.{minor} syntax")
    findings = draw_findings("def outer():\n    hash = str\n" + body)
    expected = {"builtin hash"} if reaches_builtin else set()
    assert {kind for _, _, kind in findings} == expected


def test_a_reform_factory_class_reads_a_name_it_annotates_from_the_module():
    # An annotation alone makes lib local to the class body, which then
    # reads numpy from the module, not the factory's None.
    source = (
        "import numpy as lib\n"
        "def create_reform():\n"
        "    lib = None\n"
        "    class reform_variable:\n"
        "        lib: object\n"
        "        value = lib.random.uniform()\n"
        "    return reform_variable\n"
    )
    assert [kind for _, _, kind in draw_findings(source)] == ["random source"]


# A walrus binds only if it runs: in a comprehension it may run any number
# of times, in a generator expression only as it is iterated, past the first
# operand of and, or or a chained comparison only if those reach it, and in
# a conditional expression only on its branch. So these look further out,
# here to the builtin. A walrus where it is sure to run binds.
@pytest.mark.parametrize(
    "source, reaches_builtin",
    [
        ("[(hash := str) for _ in ()]\nkey = hash('x')\n", True),
        ("g = ((hash := str) for _ in 'x')\nkey = hash('x')\nlist(g)\n", True),
        ("[v for v in '' if (hash := str)]\nkey = hash('x')\n", True),
        ("{(hash := str): v for v in ()}\nkey = hash('x')\n", True),
        ("flag = False\nflag and (hash := str)\nkey = hash('x')\n", True),
        ("flag = True\nflag or (hash := str)\nkey = hash('x')\n", True),
        ("1 < 0 < (hash := str)\nkey = hash('x')\n", True),
        ("(hash := str) if False else None\nkey = hash('x')\n", True),
        ("(hash := str)\nkey = hash('x')\n", False),
        ("(hash := str) and None\nkey = hash('x')\n", False),
        ("None if (hash := str) else None\nkey = hash('x')\n", False),
        ("[] == (hash := str)\nkey = hash('x')\n", False),
    ],
)
def test_a_walrus_that_may_not_run_binds_nothing_surely(source, reaches_builtin):
    expected = {"builtin hash"} if reaches_builtin else set()
    assert {kind for _, _, kind in draw_findings(source)} == expected


def test_a_walrus_in_an_assert_binds_nothing_surely():
    # python -O drops the assert.
    source = "assert (hash := str)\nkey = hash('x')\n"
    assert [kind for _, _, kind in draw_findings(source)] == ["builtin hash"]


def test_a_type_alias_binds_its_name():
    if sys.version_info < (3, 12):
        pytest.skip("needs Python 3.12 syntax")
    # The alias isn't callable, so Python raises before any builtin runs.
    source = "type hash = str\ntry:\n    hash('x')\nexcept TypeError:\n    pass\n"
    assert draw_findings(source) == []


# Each is the body of a function outer that binds hash = str. A global
# statement in a function sends hash to the module, and so to the builtin,
# in all the code nested in that function, classes and their methods
# included. One in a class body does so in that body and what it evaluates
# (its annotations, and its methods' defaults and annotations), but not in
# the code nested in it. Python 3.11 to 3.14 read each the same way.
@pytest.mark.parametrize(
    "body, reaches_builtin",
    [
        (
            "    def middle():\n"
            "        global hash\n"
            "        def f(x: hash('x')):\n"
            "            pass\n"
            "        f.__annotations__\n"
            "    middle()\n",
            True,
        ),
        (
            "    def middle():\n"
            "        global hash\n"
            "        def f() -> hash('x'):\n"
            "            pass\n"
            "        f.__annotations__\n"
            "    middle()\n",
            True,
        ),
        (
            "    def middle():\n"
            "        global hash\n"
            "        def f(x=hash('x')):\n"
            "            pass\n"
            "    middle()\n",
            True,
        ),
        (
            "    def middle():\n"
            "        global hash\n"
            "        def f():\n"
            "            return hash('x')\n"
            "        f()\n"
            "    middle()\n",
            True,
        ),
        (
            "    def middle():\n"
            "        global hash\n"
            "        (lambda: hash('x'))()\n"
            "    middle()\n",
            True,
        ),
        (
            "    def middle():\n"
            "        global hash\n"
            "        [hash(v) for v in 'x']\n"
            "        list(hash(v) for v in 'x')\n"
            "    middle()\n",
            True,
        ),
        (
            "    def middle():\n"
            "        global hash\n"
            "        class C:\n"
            "            key = hash('x')\n"
            "    middle()\n",
            True,
        ),
        (
            "    def middle():\n"
            "        global hash\n"
            "        class C:\n"
            "            y: hash('x') = 1\n"
            "        C.__annotations__\n"
            "    middle()\n",
            True,
        ),
        (
            "    def middle():\n"
            "        global hash\n"
            "        class C:\n"
            "            def m(self):\n"
            "                return hash('x')\n"
            "        C().m()\n"
            "    middle()\n",
            True,
        ),
        (
            "    def middle():\n"
            "        global hash\n"
            "        def inner():\n"
            "            def f():\n"
            "                return hash('x')\n"
            "            f()\n"
            "        inner()\n"
            "    middle()\n",
            True,
        ),
        # inner's global skips middle's binding too.
        (
            "    def middle():\n"
            "        hash = str\n"
            "        def inner():\n"
            "            global hash\n"
            "            def f():\n"
            "                return hash('x')\n"
            "            f()\n"
            "        inner()\n"
            "    middle()\n",
            True,
        ),
        (
            "    class C:\n"
            "        global hash\n"
            "        key = hash('x')\n"
            "        keys = [v for v in [hash('x')]]\n",
            True,
        ),
        (
            "    class C:\n"
            "        global hash\n"
            "        y: hash('x')\n"
            "    C.__annotations__\n",
            True,
        ),
        (
            "    class C:\n"
            "        global hash\n"
            "        def m(self, x: hash('x')) -> hash('y'):\n"
            "            pass\n"
            "    C.m.__annotations__\n",
            True,
        ),
        # Not in the code nested in a class body.
        (
            "    class C:\n"
            "        global hash\n"
            "        def m(self):\n"
            "            return hash('x')\n"
            "    C().m()\n",
            False,
        ),
        (
            "    class C:\n"
            "        global hash\n"
            "        keys = [hash(v) for v in 'x']\n",
            False,
        ),
        (
            "    class C:\n"
            "        global hash\n"
            "        class D:\n"
            "            key = hash('x')\n",
            False,
        ),
        (
            "    class C:\n"
            "        global hash\n"
            "        y: (lambda: hash('x'))()\n"
            "    C.__annotations__\n",
            False,
        ),
        # nonlocal names outer's hash; a nested binding is the nested code's.
        (
            "    def middle():\n"
            "        nonlocal hash\n"
            "        def f():\n"
            "            return hash('x')\n"
            "        f()\n"
            "    middle()\n",
            False,
        ),
        (
            "    def middle():\n"
            "        global hash\n"
            "        def f():\n"
            "            hash = str\n"
            "            return hash('x')\n"
            "        f()\n"
            "    middle()\n",
            False,
        ),
    ],
)
def test_global_and_nonlocal_reach_the_code_nested_in_their_scope(
    body, reaches_builtin
):
    findings = draw_findings("def outer():\n    hash = str\n" + body)
    expected = {"builtin hash"} if reaches_builtin else set()
    assert {kind for _, _, kind in findings} == expected


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


def test_star_imports_see_an_earlier_all_in_a_cycle():
    # Importing api first runs user while __all__ still lists lib.
    api = "import numpy as lib\n__all__ = ['lib']\nfrom . import user\n__all__ = []\n"
    user = "from .api import *\nlib.random.uniform()\n"
    assert _package_kinds({"api": api, "user": user}) == ["random source"]
    # Or before api sets __all__, when every public name it has bound is
    # exported.
    api = "import numpy as lib\nfrom . import user\n__all__ = []\n"
    assert _package_kinds({"api": api, "user": user}) == ["random source"]
    # A private name is exported only while an earlier __all__ lists it.
    api = "import numpy as _lib\n__all__ = ['_lib']\nfrom . import user\n__all__ = []\n"
    user = "from .api import *\n_lib.random.uniform()\n"
    assert _package_kinds({"api": api, "user": user}) == ["random source"]


@pytest.mark.parametrize(
    "api",
    [
        # Importing api first runs user before __all__ lists hash, or before
        # api binds it.
        "__all__ = []\nfrom . import user\nhash = str\n__all__ = ['hash']\n",
        "hash = str\n__all__ = []\nfrom . import user\n__all__ = ['hash']\n",
        "from . import user\nhash = str\n",
        # Through another module, a package's __init__, a function that
        # imports, or a literal dynamic import.
        "from . import other\nhash = str\n",
        "import pkg.sub.leaf\nhash = str\n",
        "def load():\n    from . import user\nload()\nhash = str\n",
        "import importlib\nimportlib.import_module('pkg.user')\nhash = str\n",
    ],
)
def test_star_imports_in_an_import_cycle_bind_nothing_surely(api):
    sources = {
        "api": api,
        "other": "from . import user\n",
        "sub": "from pkg import user\n",
        "sub.leaf": "",
        "user": "from .api import *\nkey = hash('x')\n",
    }
    assert _package_kinds(sources) == ["builtin hash"]
    # A module's star import of itself sees itself part-run too.
    itself = {"user": "from .user import *\nkey = hash('x')\nhash = str\n"}
    assert _package_kinds(itself) == ["builtin hash"]


def _modules_of(sources: dict) -> Modules:
    """Modules for {module: source}; a module with submodules is a package."""
    packages = {
        module: module
        if any(other.startswith(module + ".") for other in sources)
        else module.rsplit(".", 1)[0]
        for module in sources
    }
    return Modules(
        {
            module: (packages[module], lambda source=source: source)
            for module, source in sources.items()
        }
    )


def _assert_users_find(sources: dict, reaches_builtin: bool):
    """Each module that reads ``hash('x')`` finds the builtin, or not, in
    every order the modules are analysed in."""
    users = [module for module, source in sources.items() if "hash('x')" in source]
    expected = ["builtin hash"] if reaches_builtin else []
    for order in permutations(sources):
        modules = _modules_of(sources)
        analyses = {
            module: analyse(
                sources[module],
                f"{module}.py",
                module,
                modules.sources[module][0],
                modules,
            )
            for module in order
        }
        for user in users:
            assert [kind for _, _, kind in analyses[user].findings] == expected


# Some import order starts user while api is part-run: through the modules
# a star import of a package loads (what its __all__ lists, in any version
# of it, dotted names too, with the packages on the way, or every module
# below it where __all__ is built otherwise), or a dynamic import under
# another name or relative to the package its arguments give. In the
# controls no order does: without __all__ a star import of a package loads
# none of its submodules, one of the package around the importer starts
# nothing, as that has run, a dotted name loads only what it names, and a
# relative import's own package is the one its globals give.
@pytest.mark.parametrize(
    "sources, reaches_builtin",
    [
        (
            {
                "pkg": "__all__ = ['user']\n",
                "pkg.api": "from . import *\nhash = str\n",
                "pkg.user": "from .api import *\nkey = hash('x')\n",
            },
            True,
        ),
        (
            {
                "pkg.sub": "__all__ = ['leaf']\n",
                "pkg.sub.leaf": "from .. import user\n",
                "pkg.api": "from .sub import *\nhash = str\n",
                "pkg.user": "from .api import *\nkey = hash('x')\n",
            },
            True,
        ),
        (
            {
                "pkg.sub": "__all__ = ['user']\n",
                "pkg.sub.user": "from pkg.api import *\nkey = hash('x')\n",
                "pkg.api": "from pkg.sub import *\nhash = str\n",
            },
            True,
        ),
        # Imported first, pkg.sub imports api while its __all__ lists leaf.
        (
            {
                "pkg.sub": "__all__ = ['leaf']\nfrom .. import api\n__all__ = []\n",
                "pkg.sub.leaf": "from .. import user\n",
                "pkg.api": "from .sub import *\nhash = str\n",
                "pkg.user": "from .api import *\nkey = hash('x')\n",
            },
            True,
        ),
        (
            {
                "pkg.sub": "names = ['leaf']\n__all__ = list(names)\n",
                "pkg.sub.leaf": "from .. import user\n",
                "pkg.api": "from .sub import *\nhash = str\n",
                "pkg.user": "from .api import *\nkey = hash('x')\n",
            },
            True,
        ),
        (
            {
                "pkg.api": "from importlib import import_module as load\n"
                "load('pkg.user')\n"
                "hash = str\n",
                "pkg.user": "from .api import *\nkey = hash('x')\n",
            },
            True,
        ),
        (
            {
                "pkg.api": "import importlib\n"
                "getattr(importlib, 'import_module')('pkg.user')\n"
                "hash = str\n",
                "pkg.user": "from .api import *\nkey = hash('x')\n",
            },
            True,
        ),
        (
            {
                "pkg.sub": "",
                "pkg.sub.leaf": "from .. import user\n",
                "pkg.api": "from .sub import *\nhash = str\n",
                "pkg.user": "from .api import *\nkey = hash('x')\n",
            },
            False,
        ),
        # pkg.sub started before api, so api's star import of pkg starts no
        # module again. Python cannot bind sub, part-run, and api catches it.
        (
            {
                "pkg": "__all__ = ['sub']\n",
                "pkg.sub": "from . import user\n",
                "pkg.sub.api": "try:\n"
                "    from .. import *\n"
                "except AttributeError:\n"
                "    pass\n"
                "hash = str\n",
                "pkg.sub.user": "from .api import *\nkey = hash('x')\n",
            },
            False,
        ),
        (
            {
                "pkg.sub": "__all__ = ['user']\n",
                "pkg.sub.user": "from pkg.api import *\nkey = hash('x')\n",
                "pkg.api": "__import__('pkg.sub', fromlist=['*'])\nhash = str\n",
            },
            True,
        ),
        (
            {
                "pkg.sub": "__all__ = ['user']\n",
                "pkg.sub.user": "from pkg.api import *\nkey = hash('x')\n",
                "pkg.api": "from builtins import __import__ as load\n"
                "load('pkg.sub', fromlist=('*',))\n"
                "hash = str\n",
            },
            True,
        ),
        (
            {
                "pkg.sub": "__all__ = ['user']\n",
                "pkg.sub.user": "from pkg.api import *\nkey = hash('x')\n",
                "pkg.api": "__import__('sub', globals(), None, ['*'], 1)\nhash = str\n",
            },
            True,
        ),
        (
            {
                "pkg.sub": "__all__ = ['user']\n",
                "pkg.sub.user": "from pkg.api import *\nkey = hash('x')\n",
                "pkg.api": "__import__('pkg.sub', fromlist='*')\nhash = str\n",
            },
            True,
        ),
        (
            {
                "pkg.sub": "",
                "pkg.sub.user": "from pkg.api import *\nkey = hash('x')\n",
                "pkg.api": "__import__('pkg.sub', fromlist=['*'])\nhash = str\n",
            },
            False,
        ),
        (
            {
                "pkg.sub": "__all__ = ['branch.user']\n",
                "pkg.sub.branch": "",
                "pkg.sub.branch.user": "from pkg.api import *\nkey = hash('x')\n",
                "pkg.api": "__import__('pkg.sub', fromlist=['*'])\nhash = str\n",
            },
            True,
        ),
        # Python loads pkg.sub.branch.user, then fails to bind 'branch.user'.
        (
            {
                "pkg.sub": "__all__ = ['branch.user']\n",
                "pkg.sub.branch": "",
                "pkg.sub.branch.user": "from pkg.api import *\nkey = hash('x')\n",
                "pkg.api": "try:\n"
                "    from .sub import *\n"
                "except AttributeError:\n"
                "    pass\n"
                "hash = str\n",
            },
            True,
        ),
        (
            {
                "pkg.sub": "__all__ = ['branch.leaf']\n",
                "pkg.sub.branch": "from . import user\n",
                "pkg.sub.branch.leaf": "",
                "pkg.sub.branch.user": "from pkg.api import *\nkey = hash('x')\n",
                "pkg.api": "__import__('pkg.sub', fromlist=['*'])\nhash = str\n",
            },
            True,
        ),
        (
            {
                "pkg.sub": "names = ['branch.user']\n__all__ = list(names)\n",
                "pkg.sub.branch": "",
                "pkg.sub.branch.user": "from pkg.api import *\nkey = hash('x')\n",
                "pkg.api": "__import__('pkg.sub', fromlist=['*'])\nhash = str\n",
            },
            True,
        ),
        (
            {
                "pkg.sub": "__all__ = ['branch.other']\n",
                "pkg.sub.branch": "",
                "pkg.sub.branch.other": "",
                "pkg.sub.branch.user": "from pkg.api import *\nkey = hash('x')\n",
                "pkg.api": "__import__('pkg.sub', fromlist=['*'])\nhash = str\n",
            },
            False,
        ),
        (
            {
                "pkg.other": "",
                "pkg.other.sub": "__all__ = ['user']\n",
                "pkg.other.sub.user": "from pkg.api import *\nkey = hash('x')\n",
                "pkg.api": "__import__('sub', {'__package__': 'pkg.other'}, None, ['*'], 1)\n"
                "hash = str\n",
            },
            True,
        ),
        (
            {
                "pkg.other": "",
                "pkg.other.sub": "__all__ = ['user']\n",
                "pkg.other.sub.user": "from pkg.api import *\nkey = hash('x')\n",
                "pkg.api": "__import__('sub', {'__name__': 'pkg.other.mod'}, None, ['*'], 1)\n"
                "hash = str\n",
            },
            True,
        ),
        (
            {
                "pkg.other": "",
                "pkg.other.sub": "__all__ = ['user']\n",
                "pkg.other.sub.user": "from pkg.api import *\nkey = hash('x')\n",
                "pkg.api": "__import__(\n"
                "    'sub', {'__name__': 'pkg.other', '__path__': []}, None, ['*'], 1\n"
                ")\n"
                "hash = str\n",
            },
            True,
        ),
        # The last of a repeated key wins: __package__ is None, so __name__
        # gives the package.
        (
            {
                "pkg.other": "",
                "pkg.other.sub": "__all__ = ['user']\n",
                "pkg.other.sub.user": "from pkg.api import *\nkey = hash('x')\n",
                "pkg.api": "__import__(\n"
                "    'sub',\n"
                "    {'__package__': 'pkg', '__package__': None, '__name__': 'pkg.other.mod'},\n"
                "    None,\n"
                "    ['*'],\n"
                "    1,\n"
                ")\n"
                "hash = str\n",
            },
            True,
        ),
        # A dict fromlist is iterated by key.
        (
            {
                "pkg.other": "",
                "pkg.other.sub": "__all__ = ['user']\n",
                "pkg.other.sub.user": "from pkg.api import *\nkey = hash('x')\n",
                "pkg.api": "__import__('pkg.other.sub', fromlist={'*': None})\nhash = str\n",
            },
            True,
        ),
        # And so are a literal ``**`` or ``*`` entry's own items.
        (
            {
                "pkg.other": "",
                "pkg.other.sub": "__all__ = ['user']\n",
                "pkg.other.sub.user": "from pkg.api import *\nkey = hash('x')\n",
                "pkg.api": "__import__('pkg.other.sub', fromlist={**{'*': None}})\n"
                "hash = str\n",
            },
            True,
        ),
        (
            {
                "pkg.other": "",
                "pkg.other.sub": "__all__ = ['user']\n",
                "pkg.other.sub.user": "from pkg.api import *\nkey = hash('x')\n",
                "pkg.api": "__import__('pkg.other.sub', fromlist=[*['*']])\nhash = str\n",
            },
            True,
        ),
        (
            {
                "pkg.other": "",
                "pkg.other.sub": "__all__ = ['user']\n",
                "pkg.other.sub.user": "from pkg.api import *\nkey = hash('x')\n",
                "pkg.api": "__import__(\n"
                "    'sub', {**{'__package__': 'pkg.other'}}, None, ['*'], 1\n"
                ")\n"
                "hash = str\n",
            },
            True,
        ),
        # An empty one names nothing: no star load, so user never runs.
        (
            {
                "pkg.other": "",
                "pkg.other.sub": "__all__ = ['user']\n",
                "pkg.other.sub.user": "from pkg.api import *\nkey = hash('x')\n",
                "pkg.api": "__import__('pkg.other.sub', fromlist={**{}})\nhash = str\n",
            },
            False,
        ),
        (
            {
                "pkg.api": "import importlib\n"
                "importlib.import_module('.user', __package__)\n"
                "hash = str\n",
                "pkg.user": "from .api import *\nkey = hash('x')\n",
            },
            True,
        ),
        (
            {
                "pkg.sub": "__all__ = ['user']\n",
                "pkg.sub.user": "from pkg.api import *\nkey = hash('x')\n",
                "pkg.other": "",
                "pkg.other.sub": "__all__ = []\n",
                "pkg.api": "__import__('sub', {'__package__': 'pkg.other'}, None, ['*'], 1)\n"
                "hash = str\n",
            },
            False,
        ),
    ],
)
def test_star_imports_see_cycles_through_star_loads_and_renamed_imports(
    sources, reaches_builtin
):
    _assert_users_find({"pkg": ""} | sources, reaches_builtin)


@pytest.mark.parametrize(
    "sources, reaches_builtin",
    [
        (
            {
                "pkg": "def load():\n    from . import user\n",
                "pkg.api": "from pkg import load\nload()\nhash = str\n",
                "pkg.user": "from pkg.api import *\nkey = hash('x')\n",
            },
            True,
        ),
        (
            {
                "pkg": "from .helpers import go\ndef load():\n    go()\n",
                "pkg.helpers": "def go():\n    from . import user\n",
                "pkg.api": "from pkg import load\nload()\nhash = str\n",
                "pkg.user": "from pkg.api import *\nkey = hash('x')\n",
            },
            True,
        ),
        (
            {
                "pkg": "def load():\n    from .mid import user\n",
                "pkg.mid": "",
                "pkg.mid.api": "from pkg import load\nload()\nhash = str\n",
                "pkg.mid.user": "from pkg.mid.api import *\nkey = hash('x')\n",
            },
            True,
        ),
        (
            {
                "pkg": "def load():\n    __import__('pkg.sub', fromlist=['*'])\n",
                "pkg.api": "from pkg import load\nload()\nhash = str\n",
                "pkg.sub": "__all__ = ['user']\n",
                "pkg.sub.user": "from pkg.api import *\nkey = hash('x')\n",
            },
            True,
        ),
        (
            {
                "pkg": "load = lambda: __import__('pkg.user')\n",
                "pkg.api": "from pkg import load\nload()\nhash = str\n",
                "pkg.user": "from pkg.api import *\nkey = hash('x')\n",
            },
            True,
        ),
        (
            {
                "pkg": "loads = (__import__('pkg.user') for _ in [0])\n",
                "pkg.api": "from pkg import loads\nnext(loads)\nhash = str\n",
                "pkg.user": "from pkg.api import *\nkey = hash('x')\n",
            },
            True,
        ),
        (
            {
                "pkg": "class Loader:\n"
                "    def load(self):\n"
                "        from . import user\n",
                "pkg.api": "from pkg import Loader\nLoader().load()\nhash = str\n",
                "pkg.user": "from pkg.api import *\nkey = hash('x')\n",
            },
            True,
        ),
        (
            {
                "pkg": "from .sub import *\n",
                "pkg.sub": "__all__ = ['helpers']\n",
                "pkg.sub.helpers": "def go():\n    from .. import user\n",
                "pkg.api": "from pkg import helpers\nhelpers.go()\nhash = str\n",
                "pkg.user": "from pkg.api import *\nkey = hash('x')\n",
            },
            True,
        ),
        # pkg ran its import of other before api started; nothing api may
        # call imports user.
        (
            {
                "pkg": "from . import other\ndef load():\n    return other\n",
                "pkg.other": "VALUE = 1\n",
                "pkg.api": "from pkg import load\nload()\nhash = str\n",
                "pkg.user": "from pkg.api import *\nkey = hash('x')\n",
            },
            False,
        ),
        # pkg.mid ran, with its import of user, before api started: a
        # function's import of it starts nothing.
        (
            {
                "pkg": "def load():\n    from . import mid\n",
                "pkg.mid": "from . import user\n",
                "pkg.mid.api": "from .. import load\nhash = str\n",
                "pkg.mid.user": "from pkg.mid.api import *\nkey = hash('x')\n",
            },
            False,
        ),
    ],
)
def test_star_imports_see_cycles_through_code_the_packages_around_may_run(
    sources, reaches_builtin
):
    # The packages around a module, and what they imported as they ran, have
    # run before it, but its code may call their functions: an import in
    # one is an edge.
    _assert_users_find(sources, reaches_builtin)


# main loads pkg.helper, then api reaches it without an import, as an
# attribute of its package, and calls code in it that starts user while api
# is part-run.
@pytest.mark.parametrize(
    "api, helper",
    [
        ("import pkg\npkg.helper.go()\n", None),
        (
            "import pkg\npkg.helper.trigger\n",
            "def __getattr__(name):\n    from . import user\n",
        ),
        ("import pkg as p\np.helper.go()\n", None),
        ("import pkg\ngetattr(pkg, 'helper').go()\n", None),
        ("import sys\nsys.modules['pkg.helper'].go()\n", None),
        ("import sys\nsys.modules.get('pkg.helper').go()\n", None),
        ("__import__('pkg').helper.go()\n", None),
        ("from pkg import *\nhelper.go()\n", None),
    ],
)
def test_star_imports_see_cycles_through_modules_reached_without_an_import(api, helper):
    sources = {
        "pkg": "",
        "pkg.helper": helper or "def go():\n    from . import user\n",
        "pkg.main": "import pkg.helper\nimport pkg.api\n",
        "pkg.api": api + "hash = str\n",
        "pkg.user": "from pkg.api import *\nkey = hash('x')\n",
    }
    _assert_users_find(sources, True)


@pytest.mark.parametrize(
    "sources, reaches_builtin",
    [
        # An alias, assigned, of a package whose submodule main loaded.
        (
            {
                "pkg.sub": "",
                "pkg.sub.helper": "def go():\n    from .. import user\n",
                "pkg.main": "import pkg.sub.helper\nimport pkg.api\n",
                "pkg.api": "import pkg\nh = pkg.sub\nh.helper.go()\nhash = str\n",
                "pkg.user": "from pkg.api import *\nkey = hash('x')\n",
            },
            True,
        ),
        # An alias bound to a path below itself.
        (
            {
                "pkg.sub": "",
                "pkg.sub.helper": "def go():\n    from .. import user\n",
                "pkg.main": "import pkg.sub.helper\nimport pkg.api\n",
                "pkg.api": "import pkg\nh = pkg\nh = h.sub\nh.helper.go()\nhash = str\n",
                "pkg.user": "from pkg.api import *\nkey = hash('x')\n",
            },
            True,
        ),
        # A function in a module api imports reaches it.
        (
            {
                "pkg.helper": "def go():\n    from . import user\n",
                "pkg.x": "import pkg\ndef run():\n    pkg.helper.go()\n",
                "pkg.main": "import pkg.helper\nimport pkg.api\n",
                "pkg.api": "from pkg.x import run\nrun()\nhash = str\n",
                "pkg.user": "from pkg.api import *\nkey = hash('x')\n",
            },
            True,
        ),
        # So does a function in the package around api, by its own name for
        # its submodule.
        (
            {
                "pkg": "def load():\n    helper.go()\n",
                "pkg.helper": "def go():\n    from . import user\n",
                "pkg.main": "import pkg.helper\nimport pkg.api\n",
                "pkg.api": "from pkg import load\nload()\nhash = str\n",
                "pkg.user": "from pkg.api import *\nkey = hash('x')\n",
            },
            True,
        ),
        # The code api reaches starts nothing, or nothing that starts user.
        (
            {
                "pkg": "from . import helper\n",
                "pkg.helper": "def go():\n    return 1\n",
                "pkg.api": "import pkg\npkg.helper.go()\nhash = str\n",
                "pkg.user": "from pkg.api import *\nkey = hash('x')\n",
            },
            False,
        ),
        (
            {
                "pkg": "from . import helper\n",
                "pkg.helper": "def go():\n    from . import other\n",
                "pkg.other": "VALUE = 1\n",
                "pkg.api": "import pkg\npkg.helper.go()\nhash = str\n",
                "pkg.user": "from pkg.api import *\nkey = hash('x')\n",
            },
            False,
        ),
        # A plain module's bare name is its own, not its package's submodule.
        (
            {
                "pkg.helper": "def go():\n    from . import user\n",
                "pkg.main": "import pkg.helper\nimport pkg.api\n",
                "pkg.api": "def helper():\n    pass\nhelper()\nhash = str\n",
                "pkg.user": "from pkg.api import *\nkey = hash('x')\n",
            },
            False,
        ),
    ],
)
def test_star_imports_see_cycles_through_modules_reached_by_aliases_and_functions(
    sources, reaches_builtin
):
    _assert_users_find({"pkg": ""} | sources, reaches_builtin)


def test_a_computed_all_may_name_any_module_below_its_package():
    # __all__ holds nothing when this one runs, but a computed __all__ may
    # hold a dotted name, so a star import of the package may load any module
    # below it, and the scan errs toward reporting.
    sources = {
        "pkg": "__all__ = list([])\n",
        "pkg.sub": "from . import user\n",
        "pkg.sub.api": "from .. import *\nhash = str\n",
        "pkg.sub.user": "from .api import *\nkey = hash('x')\n",
    }
    _assert_users_find(sources, True)


@pytest.mark.parametrize(
    "source, run, later",
    [
        ("import pkg\npkg.a.f()\n", {"pkg.a"}, set()),
        ("import pkg\ndef f():\n    pkg.a.g()\n", set(), {"pkg.a"}),
        ("import pkg as p\nx = p.a\nx.b.f()\n", {"pkg.a", "pkg.a.b"}, set()),
        ("from pkg import a as b\nb.c.f()\n", {"pkg.a", "pkg.a.c"}, set()),
        ("import pkg\ng = getattr(pkg, 'a')\n", {"pkg.a"}, set()),
        ("import sys\nsys.modules['pkg.a'].f()\n", {"pkg.a"}, set()),
        ("from sys import modules\nmodules.get('pkg.a').f()\n", {"pkg.a"}, set()),
        ("f = lambda: __import__('pkg').a.f()\n", set(), {"pkg.a"}),
        # __import__ returns the top package; import_module the module.
        ("__import__('pkg.sub').a.f()\n", {"pkg.a", "pkg.sub.a"}, set()),
        ("from pkg.sub import *\na.f()\n", {"pkg.sub.a"}, set()),
        ("pkg.a.f()\n", {"pkg.a"}, set()),
        # A name bound to a path below itself.
        ("import pkg\nx = pkg\nx = x.a\nx.b.f()\n", {"pkg.a", "pkg.a.b"}, set()),
        ("import pkg\nx = pkg.a\ny = x.b\nx = y\nx.f()\n", {"pkg.a", "pkg.a.b"}, set()),
        # y's binding reads x's, bound after it.
        (
            "import pkg\nfor i in range(2):\n    y = x if i else pkg\n    x = y.a\n"
            "y.b.f()\n",
            {"pkg.a", "pkg.a.b"},
            set(),
        ),
        # Either branch, inline or bound.
        (
            "import pkg\nh = pkg.a if c else None\nh.b.f()\n",
            {"pkg.a", "pkg.a.b"},
            set(),
        ),
        ("import pkg\nh = c or pkg.a\nh.c.f()\n", {"pkg.a", "pkg.a.c"}, set()),
        ("import pkg\nh: object = pkg.a\nh.b.f()\n", {"pkg.a", "pkg.a.b"}, set()),
        (
            "import pkg\n(h := pkg.a).b.f()\nh.c\n",
            {"pkg.a", "pkg.a.b", "pkg.a.c"},
            set(),
        ),
        # A plain module's bare name is its own, not its package's submodule.
        ("a.f()\n", set(), set()),
    ],
)
def test_references_are_split_by_when_they_may_run(source, run, later):
    tree = ast.parse(source)
    (_, run_stars), (_, later_stars) = _imports_in(tree, "pkg", "pkg.m")
    modules = {"pkg.a", "pkg.a.b", "pkg.a.c", "pkg.sub.a"}
    known = {path for module in modules for path in _started(module)}
    found = _references_in(tree, "pkg", run_stars | later_stars, known, "pkg.m")
    assert (found[0] & modules, found[1] & modules) == (run, later)


@pytest.mark.parametrize(
    "source",
    [
        "import pkg\npkg.a.f()\nx.y.z\n",
        "import pkg as p\nq = p.a\nq.b.c.f()\nimport os\nos.path.join('a')\n",
        "import sys\nsys.modules['pkg.a'].f()\nsys.modules['os'].sep\ngetattr(o, 'n')\n",
    ],
)
def test_reference_paths_stay_within_the_known_paths(source):
    # Only paths a package module may yet be named from, and the names the
    # rules read, are kept, so the binding fixpoint has finitely many paths
    # to add and ends.
    modules = {"pkg.a", "pkg.a.b"}
    known = {path for module in modules for path in _started(module)}
    run, later = _references_in(ast.parse(source), "pkg", set(), known, "pkg.m")
    assert run | later <= known | REFERENCE_NAMES


# What Python imports for each call, read from its arguments.
@pytest.mark.parametrize(
    "call, imported",
    [
        ("__import__('sub', globals(), None, ['x'], 1)", ["pkg.sub", "pkg.sub.x"]),
        (
            "__import__('sub', {'__package__': 'pkg.other'}, None, (), 1)",
            ["pkg.other.sub"],
        ),
        (
            "__import__('sub', {'__package__': None, '__name__': 'pkg.o.m'}, level=1)",
            ["pkg.o.sub"],
        ),
        (
            "__import__('sub', {'__name__': 'pkg.o', '__path__': None}, level=1)",
            ["pkg.o.sub"],
        ),
        ("__import__('sub', {'__name__': 'pkg.o.m'}, level=2)", ["pkg.sub"]),
        # The last of a repeated key wins, and None then reads as absent.
        (
            "__import__('sub', {'__package__': 'pkg', '__package__': None, "
            "'__name__': 'pkg.o.m'}, level=1)",
            ["pkg.o.sub"],
        ),
        (
            "__import__('sub', {'__package__': None, '__package__': 'pkg.o'}, level=1)",
            ["pkg.o.sub"],
        ),
        ("__import__('sub', {'__name__': 'pkg.o.m', '__name__': None}, level=1)", []),
        ("__import__('sub', globals(), None, {'x': 0}, 1)", ["pkg.sub", "pkg.sub.x"]),
        # Unpacked literal entries are read in place; computed ones give none.
        (
            "__import__('sub', globals(), None, {**{'x': 0}}, 1)",
            ["pkg.sub", "pkg.sub.x"],
        ),
        (
            "__import__('sub', globals(), None, [*computed, 'x'], 1)",
            ["pkg.sub", "pkg.sub.x"],
        ),
        ("__import__('sub', {**{'__package__': 'pkg.o'}}, level=1)", ["pkg.o.sub"]),
        (
            "__import__('sub', {'__package__': 'pkg', **{'__package__': None}, "
            "'__name__': 'pkg.o.m'}, level=1)",
            ["pkg.o.sub"],
        ),
        (
            "__import__('sub', {**{'__package__': 'pkg.o'}, **other}, level=1)",
            ["pkg.sub"],
        ),
        ("__import__('sub', {1: 0, '__package__': 'pkg.o'}, level=1)", ["pkg.o.sub"]),
        # At any depth.
        (
            "__import__('sub', globals(), None, {**{**{'x': 0}}}, 1)",
            ["pkg.sub", "pkg.sub.x"],
        ),
        (
            "__import__('sub', globals(), None, [*[*['x']]], 1)",
            ["pkg.sub", "pkg.sub.x"],
        ),
        ("__import__('sub', {**{**{'__package__': 'pkg.o'}}}, level=1)", ["pkg.o.sub"]),
        (
            "__import__('sub', {'__spec__': spec, '__name__': 'x.y'}, level=1)",
            ["pkg.sub"],
        ),
        ("__import__('sub', {'__package__': computed}, level=1)", ["pkg.sub"]),
        ("__import__('sub', {'__name__': name}, level=1)", ["pkg.sub"]),
        ("__import__('sub', {**other}, level=1)", ["pkg.sub"]),
        ("__import__('sub', mapping, level=1)", ["pkg.sub"]),
        ("__import__('sub', {}, level=1)", []),
        ("import_module('.sub', __package__)", ["pkg.sub"]),
        ("import_module('.sub', package=__spec__.parent)", ["pkg.sub"]),
        ("import_module('.sub', __name__)", ["pkg.m.sub"]),
        ("import_module('..sub', 'pkg.o')", ["pkg.sub"]),
        ("import_module('.sub', computed)", ["pkg.sub"]),
        ("import_module('.sub')", []),
        ("import_module('.sub', None)", []),
    ],
)
def test_relative_dynamic_imports_resolve_as_python_reads_them(call, imported):
    node = ast.parse(call, mode="eval").body
    names = _dynamic_imports(node, DYNAMIC_IMPORTS, "pkg", "pkg.m")
    assert [name for name in names if name.startswith("pkg.")] == imported


@pytest.mark.parametrize(
    "source, run, later",
    [
        ("import pkg.a\nclass C:\n    import pkg.b\n", {"pkg.a", "pkg.b"}, set()),
        (
            "if x:\n    import pkg.a\ntry:\n    import pkg.b\nexcept E:\n    pass\n",
            {"pkg.a", "pkg.b"},
            set(),
        ),
        ("def f():\n    import pkg.a\n", set(), {"pkg.a"}),
        ("async def f():\n    import pkg.a\n", set(), {"pkg.a"}),
        ("def f():\n    if x:\n        import pkg.a\n", set(), {"pkg.a"}),
        ("class C:\n    def m(self):\n        import pkg.a\n", set(), {"pkg.a"}),
        ("f = lambda: __import__('pkg.a')\n", set(), {"pkg.a"}),
        ("g = (__import__('pkg.a') for _ in [0])\n", set(), {"pkg.a"}),
        ("x: __import__('pkg.a')\n", set(), {"pkg.a"}),
        ("def f(x: __import__('pkg.a')): pass\n", set(), {"pkg.a"}),
        ("@__import__('pkg.a')\ndef f(): pass\n", set(), {"pkg.a"}),
    ],
)
def test_imports_are_split_by_when_they_may_run(source, run, later):
    (run_names, _), (later_names, _) = _imports_in(ast.parse(source), "pkg")
    assert (run_names, later_names) == (run, later)


@pytest.mark.parametrize(
    "minor, source",
    [
        (12, "class C[T: __import__('pkg.a')]:\n    pass\n"),
        (12, "type Alias = __import__('pkg.a')\n"),
        (13, "def f[T = __import__('pkg.a')](): pass\n"),
    ],
)
def test_type_parameters_and_aliases_may_run_later(minor, source):
    if sys.version_info < (3, minor):
        pytest.skip(f"needs Python 3.{minor}")
    (run_names, _), (later_names, _) = _imports_in(ast.parse(source), "pkg")
    assert (run_names, later_names) == (set(), {"pkg.a"})


def test_imports_in_name_star_bases_by_when_they_may_run():
    source = (
        "from .sub import *\n"
        "__import__('pkg.top', fromlist=['*'])\n"
        "def f():\n    __import__('pkg.inner', fromlist='*')\n"
    )
    (_, run_stars), (_, later_stars) = _imports_in(ast.parse(source), "pkg")
    assert (run_stars, later_stars) == ({"pkg.sub", "pkg.top"}, {"pkg.inner"})


def test_star_imports_see_all_of_a_module_whose_package_imports_the_importer():
    # Importing pkg.api starts pkg first, which runs user, whose star import
    # then runs all of api: api's import of pkg starts nothing.
    sources = {
        "pkg": ("pkg", "from . import user\n"),
        "pkg.api": ("pkg", "import pkg\nhash = str\n"),
        "pkg.user": ("pkg", "from .api import *\nkey = hash('x')\n"),
    }
    modules = Modules(
        {
            module: (package, lambda source=source: source)
            for module, (package, source) in sources.items()
        }
    )
    for module, (package, source) in sources.items():
        assert analyse(source, f"{module}.py", module, package, modules).findings == []


@pytest.mark.parametrize(
    "api",
    [
        # An earlier __all__, which a module imported in a cycle sees.
        "hash = str\n__all__ = ['hash']\nfrom . import user\n__all__ = []\n",
        "hash = str\n__all__ = ['hash']\n__all__.remove('hash')\n",
        "hash = str\n__all__ = ['hash']\n__all__.remove(name)\n",
        "if flag:\n    hash = str\n",
        "hash = str\ndel hash\n",
        "hash = str\n__all__ = names()\n",
    ],
)
def test_star_imports_may_not_bind_some_names(api):
    # So the importer looks further out, here to the builtin.
    user = "from .api import *\nkey = hash('x')\n"
    assert _package_kinds({"api": api, "user": user}) == ["builtin hash"]


@pytest.mark.parametrize(
    "api",
    [
        "hash = str\n",
        "hash = str\n__all__ = ['hash']\n",
        "from .other import hash\n",
        # other doesn't import user.
        "from . import other\nhash = str\n",
    ],
)
def test_star_imports_bind_what_the_module_surely_exports(api):
    user = "from .api import *\nkey = hash('x')\n"
    sources = {"api": api, "other": "hash = str\n", "user": user}
    assert _package_kinds(sources) == []


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
    user = "policyengine_us.variables.household.person.age"
    assert "numpy" in modules.star_binds("policyengine_us.model_api", "np", user)
    assert modules.star_binds_surely("policyengine_us.model_api", "np", user)
    for api in ("policyengine_us.model_api", "policyengine_core.model_api"):
        assert "numpy.random.uniform" in modules.expand(f"{api}.np.random.uniform")
    assert "policyengine_us.model_api.all_of_variables" in modules.star_binds(
        "policyengine_us.model_api", "all_of_variables", user
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


@pytest.mark.parametrize(
    "source, offline",
    [
        (
            "from importlib import import_module\nimport_module('..taxsim', __name__)\n",
            True,
        ),
        ("__import__('taxsim', {'__name__': __name__}, None, [], 1)\n", True),
        # helper is a module, not a package: Python looks for helper.taxsim.
        (
            "from importlib import import_module\nimport_module('.taxsim', __name__)\n",
            False,
        ),
    ],
)
def test_offline_import_check_resolves_against_the_modules_name(source, offline):
    imports = analyse(
        source,
        module="policyengine_us.tools.helper",
        package="policyengine_us.tools",
    ).imports
    assert any(_is_offline(name) for _, name in imports) is offline


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
