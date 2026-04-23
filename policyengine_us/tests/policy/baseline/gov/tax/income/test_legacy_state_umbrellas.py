import pytest

from policyengine_us import Simulation
from policyengine_us.system import system


def make_tax_unit_situation(
    *,
    year: int,
    state: str,
    primary_age: int = 40,
    wages: float = 0.0,
    childcare: float = 0.0,
    rent: float = 0.0,
    dependent_ages: tuple[int, ...] = (),
):
    year_str = str(year)
    members = ["you", *[f"dependent_{i}" for i in range(1, len(dependent_ages) + 1)]]

    people = {
        "you": {
            "age": {year_str: primary_age},
            "employment_income": {year_str: wages},
            "is_tax_unit_head": {year_str: True},
            "is_tax_unit_spouse": {year_str: False},
            "is_tax_unit_dependent": {year_str: False},
            "ssi": {year_str: 0},
            "head_start": {year_str: 0},
            "early_head_start": {year_str: 0},
            "commodity_supplemental_food_program": {year_str: 0},
        }
    }

    if rent:
        people["you"]["rent"] = {year_str: rent}

    for index, age in enumerate(dependent_ages, start=1):
        name = f"dependent_{index}"
        people[name] = {
            "age": {year_str: age},
            "employment_income": {year_str: 0},
            "is_tax_unit_head": {year_str: False},
            "is_tax_unit_spouse": {year_str: False},
            "is_tax_unit_dependent": {year_str: True},
            "ssi": {year_str: 0},
            "head_start": {year_str: 0},
            "early_head_start": {year_str: 0},
            "commodity_supplemental_food_program": {year_str: 0},
        }

    tax_unit = {"members": members}
    if childcare:
        tax_unit["tax_unit_childcare_expenses"] = {year_str: childcare}

    marital_units = {"your marital unit": {"members": ["you"]}}
    for index in range(1, len(dependent_ages) + 1):
        marital_units[f"dependent_{index}_marital_unit"] = {
            "members": [f"dependent_{index}"],
            "marital_unit_id": {year_str: index},
        }

    return {
        "people": people,
        "families": {"your family": {"members": members}},
        "households": {
            "your household": {
                "members": members,
                "state_name": {year_str: state},
            }
        },
        "tax_units": {"your tax unit": tax_unit},
        "spm_units": {
            "your household": {
                "members": members,
                "snap": {year_str: 0},
                "tanf": {year_str: 0},
                "free_school_meals": {year_str: 0},
                "reduced_price_school_meals": {year_str: 0},
            }
        },
        "marital_units": marital_units,
    }


def calculate_sum(situation: dict, year: int, variables: list[str]) -> float:
    simulation = Simulation(situation=situation)
    total = 0.0

    for variable in variables:
        result = simulation.calculate(variable, period=str(year))
        if result.size != 1:
            result = simulation.calculate(variable, period=str(year), map_to="tax_unit")
        total += float(result.item())

    return total


def configured_component_vars(parameter_name: str, year: int) -> list[str]:
    parameter = getattr(system.parameters.gov.states.household, parameter_name)
    return list(parameter(f"{year}-01-01"))


LEGACY_UMBRELLA_CASES = [
    (
        "taxsim_state_agi",
        ["ok_agi"],
        make_tax_unit_situation(year=2023, state="OK", wages=40_000.0),
    ),
    (
        "taxsim_state_taxable_income",
        ["ok_taxable_income"],
        make_tax_unit_situation(year=2023, state="OK", wages=40_000.0),
    ),
    (
        "taxsim_state_cdcc",
        ["taxsim_ok_child_care_credit_component"],
        make_tax_unit_situation(
            year=2023,
            state="OK",
            wages=40_000.0,
            childcare=2_000.0,
            dependent_ages=(5,),
        ),
    ),
    (
        "taxsim_state_eitc",
        ["mn_wfc"],
        make_tax_unit_situation(
            year=2023,
            state="MN",
            wages=20_050.0,
            dependent_ages=(9, 7),
        ),
    ),
]


@pytest.mark.parametrize(
    ("legacy_var", "state_specific_vars", "situation"), LEGACY_UMBRELLA_CASES
)
def test_legacy_state_umbrellas_match_state_specific_components(
    legacy_var, state_specific_vars, situation
):
    expected = calculate_sum(situation, 2023, state_specific_vars)
    actual = calculate_sum(situation, 2023, [legacy_var])
    assert actual == pytest.approx(expected, abs=0.01)


def test_state_ctc_matches_configured_component_sum():
    situation = make_tax_unit_situation(
        year=2023,
        state="MN",
        wages=20_050.0,
        dependent_ages=(9, 7),
    )
    expected = calculate_sum(
        situation, 2023, configured_component_vars("state_ctcs", 2023)
    )
    actual = calculate_sum(situation, 2023, ["taxsim_state_ctc"])
    assert actual == pytest.approx(expected, abs=0.01)


def test_state_property_tax_credit_matches_configured_component_sum():
    situation = make_tax_unit_situation(
        year=2023,
        state="ME",
        primary_age=70,
        wages=10_000.0,
        rent=12_000.0,
    )
    expected = calculate_sum(
        situation,
        2023,
        configured_component_vars("state_property_tax_credits", 2023),
    )
    actual = calculate_sum(situation, 2023, ["taxsim_state_property_tax_credit"])
    assert actual == pytest.approx(expected, abs=0.01)


@pytest.mark.parametrize(
    ("component_vars", "combined_var", "situation"),
    [
        (
            [
                "taxsim_ok_child_care_credit_component",
                "taxsim_ok_child_tax_credit_component",
            ],
            "ok_child_care_child_tax_credit",
            make_tax_unit_situation(
                year=2023,
                state="OK",
                wages=40_000.0,
                childcare=2_000.0,
                dependent_ages=(5,),
            ),
        ),
        (
            ["mn_wfc", "taxsim_mn_child_tax_credit_component"],
            "mn_child_and_working_families_credits",
            make_tax_unit_situation(
                year=2023,
                state="MN",
                wages=20_050.0,
                dependent_ages=(9, 7),
            ),
        ),
    ],
)
def test_decomposed_credit_components_preserve_combined_credit_total(
    component_vars, combined_var, situation
):
    combined_total = calculate_sum(situation, 2023, [combined_var])
    decomposed_total = calculate_sum(situation, 2023, component_vars)
    assert decomposed_total == pytest.approx(combined_total, abs=0.01)
