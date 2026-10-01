"""Formulas must not write in place into arrays read from other variables.

policyengine-core returns the cached array itself from ``tax_unit("x",
period)``, ``tax_unit.members("x", period)`` and ``simulation.calculate``,
and ``add(entity, period, sources)`` returns that same array when
``sources`` holds a single same-entity variable. Writing into it (``x += y``, ``x[mask] = y``,
``np.place(x, ...)``, ``out=x``) changes variable ``x``'s cached value for
every later reader in the simulation, and in a branch it changes the
branch's copy. Build a new array instead: ``x = x + y``,
``x = where(mask, y, x)``.

This is a static scan. A name bound to such a call (or to an alias or
view of one) is tracked until it is rebound to anything else. Statements
are followed in source order and both sides of an ``if`` are walked, so
it can over-report; it cannot see aliasing through containers or helper
functions.
"""

import ast
from pathlib import Path

from policyengine_us.model_api import REPO

SCANNED_ROOTS = [REPO / "variables", REPO / "reforms"]

# Methods that return the cached array itself.
CACHED_ARRAY_METHODS = {"calculate", "members"}
# Methods and functions that return a view of their input.
VIEW_METHODS = {"view", "reshape", "ravel", "squeeze", "transpose"}
VIEW_FUNCTIONS = {"asarray", "asanyarray"}
# Builtins that take a string first argument but never return a cached array.
NOT_ENTITIES = {"float", "int", "str", "bool", "print", "getattr", "Path"}
# Methods that write into the array they are called on.
IN_PLACE_METHODS = {
    "fill",
    "sort",
    "resize",
    "itemset",
    "put",
    "partition",
    "byteswap",
    "setfield",
}
# numpy functions that write into their first argument.
IN_PLACE_FUNCTIONS = {
    "place",
    "putmask",
    "copyto",
    "put",
    "put_along_axis",
    "fill_diagonal",
}


def _is_string(node) -> bool:
    return isinstance(node, ast.Constant) and isinstance(node.value, str)


def _function_name(func) -> str:
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return ""


def _reads_cached_array(node, tracked) -> bool:
    """Whether ``node`` evaluates to a cached array or a view of one."""
    if isinstance(node, ast.Name):
        return node.id in tracked
    if isinstance(node, ast.IfExp):
        return _reads_cached_array(node.body, tracked) or _reads_cached_array(
            node.orelse, tracked
        )
    if isinstance(node, ast.Subscript):
        # A basic slice (x[:], x[1:]) is a view; fancy indexing copies.
        return isinstance(node.slice, ast.Slice) and _reads_cached_array(
            node.value, tracked
        )
    if isinstance(node, ast.Attribute) and node.attr in ("T", "values"):
        return _reads_cached_array(node.value, tracked)
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    name = _function_name(func)
    if isinstance(func, ast.Attribute) and name in VIEW_METHODS:
        return _reads_cached_array(func.value, tracked)
    if name in VIEW_FUNCTIONS and node.args:
        return _reads_cached_array(node.args[0], tracked)
    if name == "add" and len(node.args) >= 3:
        # add(entity, period, ["x"]) returns x's cached array itself. A
        # parameter list (add(entity, period, p.sources)) does too whenever
        # it holds a single variable, so only a literal list of two or more
        # variables is known to build a new array.
        variables = node.args[2]
        return not (
            isinstance(variables, (ast.List, ast.Tuple)) and len(variables.elts) > 1
        )
    if isinstance(func, ast.Attribute) and name == "get_array":
        return True  # holder.get_array(period)
    if not node.args or not _is_string(node.args[0]):
        return False
    if isinstance(func, ast.Name):
        # entity("x", period) or person("x", period) with person = x.members.
        return func.id not in NOT_ENTITIES and len(node.args) >= 2
    # tax_unit.members("x", period), simulation.calculate("x", period).
    # Projections such as person.tax_unit("x", period) build a new array.
    return name in CACHED_ARRAY_METHODS


def _writes_into_first_argument(func) -> bool:
    """np.place(x, ...), putmask(x, ...) or a ufunc's np.add.at(x, ...)."""
    if isinstance(func, ast.Name):
        return func.id in IN_PLACE_FUNCTIONS
    if not isinstance(func, ast.Attribute):
        return False
    if func.attr == "at":
        return True
    return (
        func.attr in IN_PLACE_FUNCTIONS
        and isinstance(func.value, ast.Name)
        and func.value.id in ("np", "numpy")
    )


def _target_names(target):
    if isinstance(target, ast.Name):
        return [target.id]
    if isinstance(target, (ast.Tuple, ast.List)):
        return [name for element in target.elts for name in _target_names(element)]
    return []


def _subscripted_name(target):
    """The array name ``x`` in ``x[...]`` or ``x.flat[...]``."""
    if not isinstance(target, ast.Subscript):
        return None
    value = target.value
    if isinstance(value, ast.Attribute) and value.attr == "flat":
        value = value.value
    return value.id if isinstance(value, ast.Name) else None


def find_in_place_writes(tree: ast.AST):
    """Return (line, function, name, how) for each in-place write found."""
    findings = []

    for function in ast.walk(tree):
        if not isinstance(function, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        tracked = set()

        def report(name, node, how):
            findings.append((node.lineno, function.name, name, how))

        def bind(target, value):
            if isinstance(target, (ast.Tuple, ast.List)) and isinstance(
                value, (ast.Tuple, ast.List)
            ):
                if len(target.elts) == len(value.elts):
                    for inner_target, inner_value in zip(target.elts, value.elts):
                        bind(inner_target, inner_value)
                    return
            reads = _reads_cached_array(value, tracked)
            for name in _target_names(target):
                if reads:
                    tracked.add(name)
                else:
                    tracked.discard(name)

        def check_calls(statement):
            for call in ast.walk(statement):
                if not isinstance(call, ast.Call):
                    continue
                func = call.func
                if (
                    isinstance(func, ast.Attribute)
                    and func.attr in IN_PLACE_METHODS
                    and isinstance(func.value, ast.Name)
                    and func.value.id in tracked
                ):
                    report(func.value.id, call, f".{func.attr}()")
                first = call.args[0] if call.args else None
                if (
                    _writes_into_first_argument(func)
                    and isinstance(first, ast.Name)
                    and first.id in tracked
                ):
                    report(first.id, call, f"{_function_name(func)}()")
                for keyword in call.keywords:
                    if (
                        keyword.arg == "out"
                        and isinstance(keyword.value, ast.Name)
                        and keyword.value.id in tracked
                    ):
                        report(keyword.value.id, call, "out=")

        def walk(statements):
            for statement in statements:
                if isinstance(
                    statement,
                    (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef),
                ):
                    continue
                # A compound statement's body is walked below; check only the
                # expressions in its header here.
                headers = [
                    getattr(statement, field)
                    for field in ("test", "iter", "subject")
                    if getattr(statement, field, None) is not None
                ] + [item.context_expr for item in getattr(statement, "items", [])]
                if not hasattr(statement, "body"):
                    headers = [statement]
                for header in headers:
                    check_calls(header)
                if isinstance(statement, ast.Assign):
                    for target in statement.targets:
                        name = _subscripted_name(target)
                        if name in tracked:
                            report(name, statement, "subscript assignment")
                    for target in statement.targets:
                        bind(target, statement.value)
                elif isinstance(statement, ast.AnnAssign) and statement.value:
                    bind(statement.target, statement.value)
                elif isinstance(statement, ast.AugAssign):
                    target = statement.target
                    if isinstance(target, ast.Name) and target.id in tracked:
                        report(target.id, statement, "augmented assignment")
                    elif _subscripted_name(target) in tracked:
                        report(
                            _subscripted_name(target),
                            statement,
                            "augmented subscript assignment",
                        )
                elif isinstance(statement, (ast.For, ast.AsyncFor)):
                    for name in _target_names(statement.target):
                        tracked.discard(name)
                for field in ("body", "orelse", "finalbody"):
                    inner = getattr(statement, field, None)
                    if isinstance(inner, list) and inner:
                        if isinstance(inner[0], ast.stmt):
                            walk(inner)
                for handler in getattr(statement, "handlers", None) or []:
                    walk(handler.body)
                for case in getattr(statement, "cases", None) or []:
                    walk(case.body)

        walk(function.body)
    return sorted(set(findings))


def scan(roots=SCANNED_ROOTS):
    violations = []
    for root in roots:
        for path in sorted(Path(root).rglob("*.py")):
            tree = ast.parse(path.read_text(), filename=str(path))
            for line, function, name, how in find_in_place_writes(tree):
                violations.append(
                    f"{path.relative_to(REPO.parent)}:{line} in {function}(): "
                    f"`{name}` ({how})"
                )
    return violations


def test_formulas_do_not_write_into_cached_arrays():
    violations = scan()
    assert not violations, (
        "These formulas write in place into an array read from another "
        "variable, which changes that variable's cached value for every "
        "later reader. Build a new array instead (x = x + y, "
        "x = where(mask, y, x)):\n" + "\n".join(violations)
    )


def _found(source: str):
    return [
        (name, how)
        for _, _, name, how in find_in_place_writes(ast.parse(source.strip()))
    ]


def test_scan_finds_in_place_writes():
    assert sorted(
        _found(
            """
def formula(tax_unit, period, parameters):
    agi = tax_unit("adjusted_gross_income", period)
    agi += 1
    person = tax_unit.members
    age = person("age", period)
    age[age > 5] = 0
    income = tax_unit.members("employment_income", period)
    income *= 2
    single = add(tax_unit, period, ["eitc"])
    single -= 1
    sources = add(tax_unit, period, p.sources)
    sources += 1
    alias = tax_unit("x", period) if parameters else tax_unit("y", period)
    view = alias.reshape(-1)
    np.place(view, view > 0, 0)
    a, b = tax_unit("a", period), tax_unit("b", period)
    np.minimum(a, 0, out=a)
    b.fill(0)
    c = simulation.calculate("c", period)
    np.add.at(c, [0], 1)
"""
        )
    ) == [
        ("a", "out="),
        ("age", "subscript assignment"),
        ("agi", "augmented assignment"),
        ("b", ".fill()"),
        ("c", "at()"),
        ("income", "augmented assignment"),
        ("single", "augmented assignment"),
        ("sources", "augmented assignment"),
        ("view", "place()"),
    ]


def test_scan_ignores_new_arrays():
    assert (
        _found(
            """
def formula(tax_unit, period, parameters):
    agi = tax_unit("adjusted_gross_income", period)
    agi = agi + 1
    agi += 1
    projected = person.tax_unit("adjusted_gross_income", period)
    projected += 1
    total = add(tax_unit, period, ["a", "b"])
    total += 1
    copied = tax_unit("x", period).copy()
    copied[copied > 0] = 0
    zip_code = pd.Series("", index=index, dtype=object)
    zip_code[mask] = "123"
    limit = float("inf")
    limit -= 1
    for value in tax_unit("x", period):
        value += 1
    rebound = tax_unit("x", period)
    if parameters:
        rebound = rebound.copy()
        np.place(rebound, rebound > 0, 0)
    other = new_array()
    other.put([0], rebound)
"""
        )
        == []
    )
