"""Reforms must be safe to apply more than once.

``CountryTaxBenefitSystem`` applies a structural reform and ``Simulation``
applies it again, so ``add_variable`` raises ``VariableNameConflictError`` the
second time. YAML tests apply a reform once and cannot detect this.
``update_variable`` adds a new variable and replaces an existing one.
"""

import ast

from policyengine_us.model_api import REPO

REFORMS_ROOT = REPO / "reforms"
NON_REPEATABLE_METHODS = {"add_variable", "add_variables"}


def calls_non_repeatable_method(node: ast.AST) -> bool:
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr in NON_REPEATABLE_METHODS
    )


def test_reforms_do_not_call_add_variable():
    violations = []

    for file_name in sorted(REFORMS_ROOT.glob("**/*.py")):
        tree = ast.parse(file_name.read_text(), filename=str(file_name))
        for node in ast.walk(tree):
            if calls_non_repeatable_method(node):
                violations.append(f"{file_name.relative_to(REPO)}:{node.lineno}")

    assert not violations, (
        "Use update_variable in reforms: a Simulation applies structural "
        "reforms a second time, and add_variable raises when it does. "
        "Violations:\n" + "\n".join(violations)
    )
