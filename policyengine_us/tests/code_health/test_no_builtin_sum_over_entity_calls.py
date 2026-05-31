import ast

from policyengine_us.model_api import REPO


VARIABLES_ROOT = REPO / "variables"
ENTITY_NAMES = {
    "person",
    "marital_unit",
    "tax_unit",
    "family",
    "spm_unit",
    "household",
}


def is_builtin_sum_call(node: ast.AST) -> bool:
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "sum"
    )


def contains_direct_entity_call(node: ast.AST) -> bool:
    return any(
        isinstance(child, ast.Call)
        and isinstance(child.func, ast.Name)
        and child.func.id in ENTITY_NAMES
        for child in ast.walk(node)
    )


def test_builtin_sum_does_not_wrap_entity_variable_calls():
    violations = []

    for file_name in sorted(VARIABLES_ROOT.glob("**/*.py")):
        tree = ast.parse(file_name.read_text(), filename=str(file_name))
        for node in ast.walk(tree):
            if is_builtin_sum_call(node) and contains_direct_entity_call(node):
                violations.append(f"{file_name.relative_to(REPO)}:{node.lineno}")

    assert not violations, (
        "Use add(entity, period, sources) or precompute arrays before "
        "calling built-in sum(); direct entity variable calls inside sum() "
        "can break vectorization. Violations:\n" + "\n".join(violations)
    )
