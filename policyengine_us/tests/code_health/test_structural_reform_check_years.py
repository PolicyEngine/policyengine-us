"""Reform factories that look ahead must share one number of years.

A factory written with its own ``range(5)`` would stop finding reforms that
every other factory finds, and nothing would report it: the reform would simply
not apply.
"""

import ast

from policyengine_us.model_api import REPO

REFORMS_ROOT = REPO / "reforms"


def is_reform_factory(node: ast.AST) -> bool:
    return (
        isinstance(node, ast.FunctionDef)
        and node.name.startswith("create_")
        and any(argument.arg == "bypass" for argument in node.args.args)
    )


def statements_outside_nested_definitions(function: ast.FunctionDef):
    pending = list(function.body)
    while pending:
        node = pending.pop()
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            continue
        yield node
        pending.extend(ast.iter_child_nodes(node))


def loops_over_another_range(node: ast.AST) -> bool:
    if not (
        isinstance(node, ast.For)
        and isinstance(node.iter, ast.Call)
        and isinstance(node.iter.func, ast.Name)
        and node.iter.func.id == "range"
    ):
        return False
    arguments = node.iter.args
    return not (
        len(arguments) == 1
        and isinstance(arguments[0], ast.Name)
        and arguments[0].id == "STRUCTURAL_REFORM_CHECK_YEARS"
    )


def test_reform_factories_use_the_shared_number_of_years():
    violations = []

    for file_name in sorted(REFORMS_ROOT.glob("**/*.py")):
        tree = ast.parse(file_name.read_text(), filename=str(file_name))
        for factory in filter(is_reform_factory, ast.walk(tree)):
            for node in statements_outside_nested_definitions(factory):
                if loops_over_another_range(node):
                    violations.append(f"{file_name.relative_to(REPO)}:{node.lineno}")

    assert not violations, (
        "Loop over range(STRUCTURAL_REFORM_CHECK_YEARS) in reform factories. "
        "Violations:\n" + "\n".join(violations)
    )
