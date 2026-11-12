import ast

from policyengine_us.model_api import REPO


VARIABLES_ROOT = REPO / "variables"
PERIOD_OPTIONS = {"ADD", "DIVIDE"}


def passes_period_option(node: ast.AST) -> bool:
    if not isinstance(node, ast.Call):
        return False
    return any(
        keyword.arg == "options"
        and any(
            isinstance(child, ast.Name) and child.id in PERIOD_OPTIONS
            for child in ast.walk(keyword.value)
        )
        for keyword in node.keywords
    )


def test_entity_calls_do_not_pass_add_or_divide_options():
    violations = []

    for file_name in sorted(VARIABLES_ROOT.glob("**/*.py")):
        tree = ast.parse(file_name.read_text(), filename=str(file_name))
        for node in ast.walk(tree):
            if passes_period_option(node):
                violations.append(f"{file_name.relative_to(REPO)}:{node.lineno}")

    assert not violations, (
        "Read the variable with the bare period, or use add(entity, period, "
        "sources): Core already sums a monthly variable over a year and "
        "divides a yearly one over a month. options=[ADD] and "
        "options=[DIVIDE] raise a TypeError in a Microsimulation, whose "
        "calculate_add and calculate_divide do not accept the decode_enums "
        "keyword that an entity call passes, so household tests pass while "
        "the formula fails over microdata. Violations:\n" + "\n".join(violations)
    )
