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


def loops_over_a_literal_range(node: ast.AST) -> bool:
    return (
        isinstance(node, ast.For)
        and isinstance(node.iter, ast.Call)
        and isinstance(node.iter.func, ast.Name)
        and node.iter.func.id == "range"
        and any(isinstance(argument, ast.Constant) for argument in node.iter.args)
    )


def test_reform_factories_use_the_shared_number_of_years():
    violations = []

    for file_name in sorted(REFORMS_ROOT.glob("**/*.py")):
        tree = ast.parse(file_name.read_text(), filename=str(file_name))
        for factory in filter(is_reform_factory, ast.walk(tree)):
            for node in ast.walk(factory):
                if loops_over_a_literal_range(node):
                    violations.append(f"{file_name.relative_to(REPO)}:{node.lineno}")

    assert not violations, (
        "Loop over range(STRUCTURAL_REFORM_CHECK_YEARS) in reform factories. "
        "Violations:\n" + "\n".join(violations)
    )
