"""Compare Idaho premium election with independently enumerated legal routes."""

from hypothesis import example, given, settings, strategies as st
import pytest

from policyengine_us import Simulation
from policyengine_us.system import system as SYSTEM


PERIOD = "2026"
AMOUNT = st.integers(min_value=0, max_value=50_000)
ROW = st.fixed_dictionaries(
    {
        "premiums": st.tuples(AMOUNT, AMOUNT),
        "pre_tax": st.tuples(AMOUNT, AMOUNT),
        "above_line": AMOUNT,
        "dependent_above_line": AMOUNT,
        "medical": AMOUNT,
        "standard": AMOUNT,
        "itemized": AMOUNT,
        "mandatory": st.booleans(),
    }
)


@settings(max_examples=20, deadline=None)
@given(rows=st.lists(ROW, min_size=2, max_size=5))
@example(
    rows=[
        {
            "premiums": (1_000, 500),
            "pre_tax": (0, 0),
            "above_line": 0,
            "dependent_above_line": 0,
            "medical": 500,
            "standard": 10_000,
            "itemized": 10_500,
            "mandatory": False,
        },
        {
            "premiums": (0, 0),
            "pre_tax": (0, 0),
            "above_line": 0,
            "dependent_above_line": 0,
            "medical": 0,
            "standard": 10_000,
            "itemized": 1_000,
            "mandatory": True,
        },
    ]
)
def test_premium_subtraction_and_election_match_best_legal_route(rows):
    people = {}
    tax_units = {}
    households = {}
    expected_itemizes = []
    expected_subtractions = []
    expected_reductions = []
    available_premiums = []
    for index, row in enumerate(rows):
        members = [f"person_{index}_{member}" for member in range(2)]
        for member, person_id in enumerate(members):
            people[person_id] = {
                "age": {PERIOD: 35},
                "health_insurance_premiums": {PERIOD: row["premiums"][member]},
                "pre_tax_health_insurance_premiums": {PERIOD: row["pre_tax"][member]},
            }
        tax_units[f"tax_unit_{index}"] = {
            "members": members,
            "self_employed_health_insurance_ald": {PERIOD: row["above_line"]},
            "dependents_self_employed_health_insurance_ald": {
                PERIOD: row["dependent_above_line"]
            },
            "medical_expense_deduction": {PERIOD: row["medical"]},
            "standard_deduction": {PERIOD: row["standard"]},
            "id_itemized_deductions": {PERIOD: row["itemized"]},
            "separate_filer_itemizes": {PERIOD: row["mandatory"]},
        }
        households[f"household_{index}"] = {
            "members": members,
            "state_code": {PERIOD: "ID"},
        }

        # Enumerate the standard and itemized routes using scalar arithmetic.
        # Their combined reduction, rather than deduction alone, determines
        # the favorable election; a spouse's itemization overrides that choice.
        available = max(
            0,
            sum(row["premiums"])
            - sum(row["pre_tax"])
            - row["above_line"]
            - row["dependent_above_line"],
        )
        unclaimed_if_itemizing = max(0, available - row["medical"])
        standard_route = (row["standard"] + available, False, available)
        itemized_route = (
            row["itemized"] + unclaimed_if_itemizing,
            True,
            unclaimed_if_itemizing,
        )
        elected = (
            itemized_route
            if row["mandatory"]
            else max((standard_route, itemized_route), key=lambda route: route[0])
        )
        expected_reductions.append(elected[0])
        expected_itemizes.append(elected[1])
        expected_subtractions.append(elected[2])
        available_premiums.append(available)

    simulation = Simulation(
        tax_benefit_system=SYSTEM,
        situation={
            "people": people,
            "tax_units": tax_units,
            "households": households,
        },
    )
    subtraction = simulation.calculate(
        "id_health_insurance_premiums_subtraction", PERIOD
    )
    deductions = simulation.calculate("id_deductions", PERIOD)

    assert simulation.calculate("id_itemizes", PERIOD).tolist() == expected_itemizes
    assert subtraction.tolist() == pytest.approx(expected_subtractions)
    assert (deductions + subtraction).tolist() == pytest.approx(expected_reductions)
    assert all(
        0 <= actual <= available
        for actual, available in zip(subtraction, available_premiums)
    )
