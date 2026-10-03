"""Formulas must not write in place into arrays read from other variables.

policyengine-core returns the cached array itself from ``tax_unit("x",
period)``, ``tax_unit.members("x", period)`` and ``simulation.calculate``,
and ``add(entity, period, sources)`` returns that same array when
``sources`` holds a single same-entity variable. Writing into it (``x += y``,
``x[mask] = y``, ``np.place(x, ...)``, ``out=x``) changes variable ``x``'s
cached value for every later reader in the simulation, and in a branch it
changes the branch's copy. Build a new array instead: ``x = x + y``,
``x = where(mask, y, x)``.

This is a static scan. A name bound to such a call, or to an alias or view
of one, is tracked until it is rebound to anything else. The two sides of an
``if``, the cases of a ``match`` and the parts of a ``try`` are walked from
the same incoming state and merged afterwards, and loop bodies are walked
as if they ran zero, one or two times, so a name counts as a cached array
after a branch if it is one on any path. It can over-report (``np.asarray``
with a new dtype copies, but is treated as a view); it cannot see aliasing
through containers or helper functions.
"""

import ast
from pathlib import Path

from policyengine_us.model_api import REPO

SCANNED_ROOTS = [REPO / "variables", REPO / "reforms"]

# Names formulas use for entities: calling one returns a cached array.
ENTITY_NAMES = {
    "person",
    "tax_unit",
    "spm_unit",
    "household",
    "family",
    "marital_unit",
}
# Methods that return the cached array itself.
CACHED_ARRAY_METHODS = {"calculate", "members"}
# Methods and functions that return a view of their input.
VIEW_METHODS = {"view", "reshape", "ravel", "squeeze", "transpose"}
VIEW_FUNCTIONS = {"asarray", "asanyarray"}
VIEW_ATTRIBUTES = {"T", "values", "flat"}
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


def _reads_cached_array(node, tracked, entities) -> bool:
    """Whether ``node`` evaluates to a cached array or a view of one."""
    if isinstance(node, ast.Name):
        return node.id in tracked
    if isinstance(node, ast.IfExp):
        return _reads_cached_array(node.body, tracked, entities) or _reads_cached_array(
            node.orelse, tracked, entities
        )
    if isinstance(node, ast.Subscript):
        # A basic slice (x[:], x[1:]) is a view; fancy indexing copies.
        return isinstance(node.slice, ast.Slice) and _reads_cached_array(
            node.value, tracked, entities
        )
    if isinstance(node, ast.Attribute) and node.attr in VIEW_ATTRIBUTES:
        return _reads_cached_array(node.value, tracked, entities)
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    name = _function_name(func)
    if isinstance(func, ast.Attribute) and name in VIEW_METHODS:
        return _reads_cached_array(func.value, tracked, entities)
    if name in VIEW_FUNCTIONS and node.args:
        return _reads_cached_array(node.args[0], tracked, entities)
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
    if isinstance(func, ast.Attribute):
        # tax_unit.members(name, period), simulation.calculate(name, period).
        # Projections such as person.tax_unit("x", period) build a new array.
        return name in CACHED_ARRAY_METHODS and bool(node.args)
    if isinstance(func, ast.Name) and len(node.args) >= 2:
        # entity(name, period), including a variable name held in a name;
        # or any other callable given a variable name as a string.
        return func.id in entities or (
            _is_string(node.args[0]) and func.id not in NOT_ENTITIES
        )
    return False


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


def _byteswaps_in_place(call) -> bool:
    """x.byteswap() returns a copy unless asked to swap in place."""
    flags = list(call.args[:1]) + [
        keyword.value for keyword in call.keywords if keyword.arg == "inplace"
    ]
    return any(
        not (isinstance(flag, ast.Constant) and not flag.value) for flag in flags
    )


def _target_names(target):
    if isinstance(target, ast.Name):
        return [target.id]
    if isinstance(target, (ast.Tuple, ast.List, ast.Starred)):
        elements = target.elts if hasattr(target, "elts") else [target.value]
        return [name for element in elements for name in _target_names(element)]
    return []


def find_in_place_writes(tree: ast.AST):
    """Return (line, function, array, how) for each in-place write found."""
    findings = set()

    for function in ast.walk(tree):
        if not isinstance(function, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        entities = set(ENTITY_NAMES)
        if function.name.startswith("formula") and function.args.args:
            entities.add(function.args.args[0].arg)

        def cached(node, tracked):
            return _reads_cached_array(node, tracked, entities)

        def report(array, node, how):
            findings.add((node.lineno, function.name, ast.unparse(array), how))

        def bind(target, value, tracked):
            if isinstance(target, (ast.Tuple, ast.List)) and isinstance(
                value, (ast.Tuple, ast.List)
            ):
                if len(target.elts) == len(value.elts):
                    for inner_target, inner_value in zip(target.elts, value.elts):
                        bind(inner_target, inner_value, tracked)
                    return
            if (
                isinstance(target, ast.Name)
                and isinstance(value, ast.Attribute)
                and value.attr == "members"
            ):
                entities.add(target.id)  # person = tax_unit.members
            reads = cached(value, tracked)
            for name in _target_names(target):
                if reads:
                    tracked.add(name)
                else:
                    tracked.discard(name)

        def check_target(target, statement, tracked, how):
            if isinstance(target, ast.Subscript) and cached(target.value, tracked):
                report(target.value, statement, how)

        def check_calls(node, tracked):
            for call in ast.walk(node):
                if not isinstance(call, ast.Call):
                    continue
                func = call.func
                if isinstance(func, ast.Attribute) and cached(func.value, tracked):
                    if func.attr in IN_PLACE_METHODS or (
                        func.attr == "byteswap" and _byteswaps_in_place(call)
                    ):
                        report(func.value, call, f".{func.attr}()")
                first = call.args[0] if call.args else None
                if (
                    first is not None
                    and _writes_into_first_argument(func)
                    and cached(first, tracked)
                ):
                    report(first, call, f"{_function_name(func)}()")
                for keyword in call.keywords:
                    if keyword.arg != "out":
                        continue
                    outputs = (
                        keyword.value.elts
                        if isinstance(keyword.value, ast.Tuple)
                        else [keyword.value]
                    )
                    for output in outputs:
                        if cached(output, tracked):
                            report(output, call, "out=")

        def walk(statements, tracked):
            """Walk statements from ``tracked``; return the names tracked after."""
            tracked = set(tracked)
            for statement in statements:
                if isinstance(
                    statement,
                    (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef),
                ):
                    continue
                if isinstance(statement, ast.If):
                    check_calls(statement.test, tracked)
                    tracked = walk(statement.body, tracked) | walk(
                        statement.orelse, tracked
                    )
                elif isinstance(statement, (ast.For, ast.AsyncFor, ast.While)):
                    header = getattr(statement, "iter", None) or statement.test
                    check_calls(header, tracked)
                    loop_names = _target_names(getattr(statement, "target", None))
                    start = tracked - set(loop_names)
                    once = walk(statement.body, start)
                    twice = walk(statement.body, start | once)
                    tracked = walk(statement.orelse, tracked | once | twice)
                elif isinstance(statement, (ast.With, ast.AsyncWith)):
                    for item in statement.items:
                        check_calls(item.context_expr, tracked)
                    tracked = walk(statement.body, tracked)
                elif isinstance(statement, ast.Try) or (
                    type(statement).__name__ == "TryStar"
                ):
                    body = walk(statement.body, tracked)
                    after = set(body)
                    for handler in statement.handlers:
                        after |= walk(handler.body, tracked | body)
                    after |= walk(statement.orelse, body)
                    tracked = walk(statement.finalbody, after | tracked)
                elif isinstance(statement, ast.Match):
                    check_calls(statement.subject, tracked)
                    after = set(tracked)
                    for case in statement.cases:
                        after |= walk(case.body, tracked)
                    tracked = after
                else:
                    check_calls(statement, tracked)
                    if isinstance(statement, ast.Assign):
                        for target in statement.targets:
                            check_target(
                                target, statement, tracked, "subscript assignment"
                            )
                        for target in statement.targets:
                            bind(target, statement.value, tracked)
                    elif isinstance(statement, ast.AnnAssign) and statement.value:
                        bind(statement.target, statement.value, tracked)
                    elif isinstance(statement, ast.AugAssign):
                        target = statement.target
                        if isinstance(target, ast.Name) and target.id in tracked:
                            report(target, statement, "augmented assignment")
                        check_target(
                            target,
                            statement,
                            tracked,
                            "augmented subscript assignment",
                        )
            return tracked

        walk(function.body, set())
    return sorted(findings)


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
    d = tax_unit("d", period)
    d.reshape(-1)[:] += 1
    np.copyto(d[:], 0)
    np.add(d, 1, out=d[:])
    d.flat[0] = 1
    d.byteswap(inplace=True)
    for name in names:
        e = tax_unit(name, period)
        e[e > 0] = 0
    f = person.spm_unit.members(name, period)
    f += 1
"""
        )
    ) == [
        ("a", "out="),
        ("age", "subscript assignment"),
        ("agi", "augmented assignment"),
        ("b", ".fill()"),
        ("c", "at()"),
        ("d", ".byteswap()"),
        ("d.flat", "subscript assignment"),
        ("d.reshape(-1)", "augmented subscript assignment"),
        ("d[:]", "copyto()"),
        ("d[:]", "out="),
        ("e", "subscript assignment"),
        ("f", "augmented assignment"),
        ("income", "augmented assignment"),
        ("single", "augmented assignment"),
        ("sources", "augmented assignment"),
        ("view", "place()"),
    ]


def test_scan_follows_every_path_through_branches_and_loops():
    assert sorted(
        _found(
            """
def formula(tax_unit, period, parameters):
    optional_copy = tax_unit("x", period)
    if parameters.copy:
        optional_copy = optional_copy.copy()
    optional_copy += 1
    either = tax_unit("x", period)
    if parameters.cached:
        either = tax_unit("y", period)
    else:
        either = np.zeros(3)
    either += 1
    loop = np.zeros(3)
    for _ in range(3):
        loop += 1
        loop = tax_unit("x", period)
    caught = np.zeros(3)
    try:
        caught = tax_unit("x", period)
    except KeyError:
        pass
    caught[0] = 1
"""
        )
    ) == [
        ("caught", "subscript assignment"),
        ("either", "augmented assignment"),
        ("loop", "augmented assignment"),
        ("optional_copy", "augmented assignment"),
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
    swapped = tax_unit("x", period)
    swapped = swapped.byteswap()
    swapped += 1
    both = tax_unit("x", period)
    if parameters:
        both = both.copy()
    else:
        both = both + 0
    both += 1
"""
        )
        == []
    )
