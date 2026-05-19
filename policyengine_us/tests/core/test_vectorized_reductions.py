import ast
from pathlib import Path

import pytest

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


def test_tanf_non_cash_asset_test_applies_texas_additional_vehicle_exemption():
    simulation = Simulation(
        situation=_two_person_two_household_situation(
            person_a={"age": {"2026": 30}},
            person_b={"age": {"2026": 40}},
            state="TX",
        )
    )
    simulation.set_input("snap_assets", 2026, [4_000, 4_000])
    simulation.set_input("household_vehicles_value", 2026, [31_200, 32_300])
    simulation.set_input("household_vehicles_owned", 2026, [2, 2])

    assert simulation.calculate(
        "meets_tanf_non_cash_asset_test", "2026-01"
    ).tolist() == [
        True,
        False,
    ]


def test_county_mixed_known_and_missing_fips_preserves_known_rows():
    simulation = Simulation(
        situation=_two_person_two_household_situation(
            person_a={"age": {"2025": 30}},
            person_b={"age": {"2025": 40}},
        )
    )
    simulation.set_input("state_code", 2025, ["NY", "CA"])
    simulation.set_input("county_fips", 2025, ["36059", ""])

    assert simulation.calculate("county_str", 2025).tolist() == [
        "NASSAU_COUNTY_NY",
        "ALAMEDA_COUNTY_CA",
    ]


def test_county_all_missing_fips_uses_state_fallback():
    simulation = Simulation(
        situation=_two_person_two_household_situation(
            person_a={"age": {"2025": 30}},
            person_b={"age": {"2025": 40}},
        )
    )
    simulation.set_input("state_code", 2025, ["NY", "CA"])
    simulation.set_input("county_fips", 2025, ["", ""])

    assert simulation.calculate("county_str", 2025).tolist() == [
        "ALBANY_COUNTY_NY",
        "ALAMEDA_COUNTY_CA",
    ]


def test_il_aabd_utility_allowance_uses_elementwise_caps():
    simulation = Simulation(
        situation=_two_person_two_household_situation(
            person_a={"age": {"2022": 30}},
            person_b={"age": {"2022": 40}},
            state="IL",
        )
    )
    simulation.set_input("state_code", 2022, ["IL", "IL"])
    simulation.set_input("county_str", 2022, ["COOK_COUNTY_IL", "BOND_COUNTY_IL"])
    simulation.set_input("water_expense", 2022, [60, 0])
    simulation.set_input("coal_expense", 2022, [0, 144])

    assert simulation.calculate(
        "il_aabd_utility_allowance", "2022-01"
    ).tolist() == pytest.approx([3.8, 11.1])


def test_co_ccap_unknown_county_fallback_is_row_specific():
    simulation = Simulation(
        situation=_two_person_two_household_situation(
            person_a={"age": {"2023": 30}},
            person_b={"age": {"2023": 40}},
            state="CO",
        )
    )
    simulation.set_input("state_code", 2023, ["CO", "CO"])
    simulation.set_input("county_str", 2023, ["BACA_COUNTY_CO", "UNKNOWN"])
    simulation.set_input("co_ccap_countable_income", 2023, [30 * 12, 0])
    simulation.set_input("spm_unit_fpg", 2023, [12 * 12, 12 * 12])

    assert simulation.calculate("co_ccap_fpg_eligible", "2023-01").tolist() == [
        False,
        True,
    ]
