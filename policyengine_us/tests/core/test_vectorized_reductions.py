import ast
from pathlib import Path

from policyengine_us import Simulation


def _two_person_two_household_situation(
    person_a: dict,
    person_b: dict,
    *,
    state: str = "CA",
) -> dict:
    return {
        "people": {
            "a": person_a,
            "b": person_b,
        },
        "tax_units": {
            "tax_unit_a": {"members": ["a"]},
            "tax_unit_b": {"members": ["b"]},
        },
        "spm_units": {
            "spm_unit_a": {"members": ["a"]},
            "spm_unit_b": {"members": ["b"]},
        },
        "families": {
            "family_a": {"members": ["a"]},
            "family_b": {"members": ["b"]},
        },
        "households": {
            "household_a": {"members": ["a"], "state_code": {"2026": state}},
            "household_b": {"members": ["b"], "state_code": {"2026": state}},
        },
    }


def test_is_usda_disabled_reduces_per_person_not_across_simulation():
    simulation = Simulation(
        situation=_two_person_two_household_situation(
            person_a={"age": {"2026": 30}},
            person_b={
                "age": {"2026": 40},
                "social_security_disability": {"2026": 100},
            },
        )
    )

    assert simulation.calculate("is_usda_disabled", 2026).tolist() == [
        False,
        True,
    ]


def test_medicaid_medically_needy_category_reduces_per_person():
    simulation = Simulation(
        situation=_two_person_two_household_situation(
            person_a={"age": {"2026": 30}},
            person_b={"age": {"2026": 70}},
        )
    )

    assert simulation.calculate(
        "is_in_medicaid_medically_needy_category", 2026
    ).tolist() == [
        False,
        True,
    ]


def test_has_qdiv_or_ltcg_reduces_per_tax_unit_not_across_simulation():
    simulation = Simulation(
        situation=_two_person_two_household_situation(
            person_a={"age": {"2026": 30}},
            person_b={
                "age": {"2026": 40},
                "qualified_dividend_income": {"2026": 100},
            },
        )
    )

    assert simulation.calculate("has_qdiv_or_ltcg", 2026).tolist() == [
        False,
        True,
    ]


def test_numpy_any_all_outputs_specify_axis_or_stay_in_control_flow():
    variables_dir = Path(__file__).parents[2] / "variables"
    offenders = []

    for path in variables_dir.rglob("*.py"):
        tree = ast.parse(path.read_text())
        parents = {}
        for parent in ast.walk(tree):
            for child in ast.iter_child_nodes(parent):
                parents[child] = parent

        for node in ast.walk(tree):
            if not (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr in {"any", "all"}
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "np"
            ):
                continue

            if any(keyword.arg == "axis" for keyword in node.keywords):
                continue

            parent = parents.get(node)
            in_control_flow_test = False
            while parent is not None:
                if isinstance(parent, (ast.If, ast.While)):
                    in_control_flow_test = node in ast.walk(parent.test)
                    break
                parent = parents.get(parent)

            if not in_control_flow_test:
                offenders.append(f"{path.relative_to(variables_dir)}:{node.lineno}")

    assert offenders == []


def test_tanf_non_cash_asset_test_does_not_mutate_snap_assets():
    simulation = Simulation(
        situation=_two_person_two_household_situation(
            person_a={"age": {"2026": 30}},
            person_b={"age": {"2026": 40}},
            state="TX",
        )
    )
    simulation.set_input("snap_assets", 2026, [4_000, 4_000])
    simulation.set_input("household_vehicles_value", 2026, [24_000, 0])

    simulation.calculate("meets_tanf_non_cash_asset_test", "2026-01")

    assert simulation.calculate("snap_assets", "2026-01").tolist() == [
        4_000,
        4_000,
    ]
