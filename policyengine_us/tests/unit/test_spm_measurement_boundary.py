"""Keep SPM valuation caps out of policy benefits and general income measures."""

import ast
from pathlib import Path

import yaml


def test_spm_caps_have_only_spm_resource_consumers():
    root = Path(__file__).resolve().parents[2]
    # New reporting leaves require an explicit update to this allowed graph.
    consumers = {
        "spm_unit_allocated_housing_subsidy": {"spm_unit_capped_housing_subsidy"},
        "spm_unit_allocated_tenant_payment": {"spm_unit_capped_housing_subsidy"},
        "spm_unit_capped_housing_subsidy": {"spm_unit_benefits"},
        "spm_unit_capped_work_childcare_expenses": {"spm_unit_spm_expenses"},
        "spm_unit_head_spouse_earned_cap": {"spm_unit_capped_work_childcare_expenses"},
        "spm_unit_spm_expenses": {"spm_unit_net_income"},
        "spm_unit_benefits": {"spm_unit_net_income"},
        "spm_unit_net_income": {
            "spm_unit_is_in_spm_poverty",
            "spm_unit_is_in_deep_spm_poverty",
            "poverty_gap",
            "deep_poverty_gap",
            "spm_unit_oecd_equiv_net_income",
        },
        "spm_unit_oecd_equiv_net_income": {"spm_unit_income_decile"},
        "spm_unit_income_decile": set(),
        "poverty_gap": {"in_poverty"},
        "deep_poverty_gap": {"in_deep_poverty"},
        "spm_unit_is_in_spm_poverty": set(),
        "spm_unit_is_in_deep_spm_poverty": set(),
        "in_poverty": {"person_in_poverty"},
        "in_deep_poverty": set(),
        "person_in_poverty": set(),
    }
    violations = []

    class Visitor(ast.NodeVisitor):
        def __init__(self, path):
            self.path = path
            self.consumer = None

        def visit_ClassDef(self, node):
            previous = self.consumer
            self.consumer = node.name
            self.generic_visit(node)
            self.consumer = previous

        def visit_Constant(self, node):
            if isinstance(node.value, str) and node.value in consumers:
                # References outside a variable class also fail explicitly.
                if self.consumer not in consumers[node.value]:
                    violations.append(
                        f"{self.path.relative_to(root)}:{node.lineno}: "
                        f"{self.consumer} consumes {node.value}"
                    )

        def visit_Expr(self, node):
            # A docstring describes a variable; it does not calculate one.
            if not isinstance(node.value, ast.Constant) or not isinstance(
                node.value.value, str
            ):
                self.generic_visit(node)

        def visit_Assign(self, node):
            metadata = {"documentation", "label", "reference"}
            if not all(
                isinstance(target, ast.Name) and target.id in metadata
                for target in node.targets
            ):
                self.generic_visit(node)

    for directory in ("variables", "reforms"):
        for path in (root / directory).rglob("*.py"):
            Visitor(path).visit(ast.parse(path.read_text(), filename=str(path)))

    def scalar_values(value):
        if isinstance(value, dict):
            for key, child in value.items():
                if key == "description":
                    continue
                if key == "metadata":
                    # A breakdown can name a variable; descriptive metadata
                    # cannot introduce a calculated dependency.
                    if isinstance(child, dict):
                        yield from scalar_values(child.get("breakdown", []))
                    continue
                yield from scalar_values(child)
        elif isinstance(value, list):
            for child in value:
                yield from scalar_values(child)
        else:
            yield value

    # Include nested values in brackets/breakdowns. BaseLoader preserves
    # year-zero date keys without constructing unsupported datetime objects.
    for path in (root / "parameters").rglob("*.yaml"):
        parameter = yaml.load(path.read_text(), Loader=yaml.BaseLoader)
        for value in scalar_values(parameter):
            if value in consumers:
                violations.append(f"{path.relative_to(root)} names {value}")

    assert not violations, "\n".join(violations)
