"""Compare Idaho premium election with independently enumerated legal routes."""

from importlib.metadata import version

from hypothesis import example, given, settings, strategies as st
import numpy as np
from packaging.version import Version
import pytest

from policyengine_us import Simulation
from policyengine_us.system import system as SYSTEM


PERIOD = "2026"
AMOUNT = st.integers(min_value=0, max_value=50_000)
ROW = st.fixed_dictionaries(
    {
        "premiums": st.tuples(AMOUNT, AMOUNT, AMOUNT),
        "pre_tax": st.tuples(AMOUNT, AMOUNT, AMOUNT),
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
            "premiums": (1_000, 500, 1_000),
            "pre_tax": (0, 0, 0),
            "above_line": 0,
            "dependent_above_line": 900,
            "medical": 500,
            "standard": 10_000,
            "itemized": 10_500,
            "mandatory": False,
        },
        {
            "premiums": (0, 0, 500),
            "pre_tax": (0, 0, 0),
            "above_line": 0,
            "dependent_above_line": 0,
            "medical": 0,
            "standard": 10_000,
            "itemized": 1_000,
            "mandatory": True,
        },
    ]
)
@example(
    rows=[
        {
            "premiums": (1_000, 0, 500),
            "pre_tax": (0, 0, 0),
            "above_line": 0,
            "dependent_above_line": 0,
            "medical": 0,
            "standard": 16_100,
            "itemized": 0,
            "mandatory": False,
        },
        {
            "premiums": (1_000, 0, 500),
            "pre_tax": (0, 0, 0),
            "above_line": 0,
            "dependent_above_line": 500,
            "medical": 0,
            "standard": 16_100,
            "itemized": 0,
            "mandatory": False,
        },
        {
            "premiums": (1_000, 400, 500),
            "pre_tax": (100, 50, 500),
            "above_line": 150,
            "dependent_above_line": 500,
            "medical": 0,
            "standard": 16_100,
            "itemized": 0,
            "mandatory": False,
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
        members = [f"person_{index}_{member}" for member in range(3)]
        for member, person_id in enumerate(members):
            people[person_id] = {
                "age": {PERIOD: (40, 39, 20)[member]},
                "is_tax_unit_head": {PERIOD: member == 0},
                "is_tax_unit_spouse": {PERIOD: member == 1},
                "is_tax_unit_dependent": {PERIOD: member == 2},
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
        # Premium inputs identify the payer: only the head and spouse's
        # payments enter this return. The dependent's payments and deductions
        # belong on the dependent's own return. Pretax payroll premiums are
        # a separate leaf input and never reduce these after-tax payments.
        # The explicit pretax example has 1,000 + 400 - 150 = 1,250 available,
        # irrespective of its separate 100 + 50 = 150 pretax premiums.
        # Its standard route retains 1,250 and reduces income by
        # 16,100 + 1,250 = 17,350, exceeding itemized 0 + 1,250 = 1,250.
        available = max(
            0,
            sum(row["premiums"][:2]) - row["above_line"],
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

    assert simulation.calculate(
        "id_qualified_health_insurance_premiums", PERIOD
    ).tolist() == pytest.approx(available_premiums)
    assert simulation.calculate("id_itemizes", PERIOD).tolist() == expected_itemizes
    assert subtraction.tolist() == pytest.approx(expected_subtractions)
    assert (deductions + subtraction).tolist() == pytest.approx(expected_reductions)
    assert all(
        0 <= actual <= available
        for actual, available in zip(subtraction, available_premiums)
    )


def test_actual_medical_deduction_is_scoped_to_period_and_branch():
    years = (2025, 2026)
    simulation = Simulation(
        tax_benefit_system=SYSTEM,
        situation={
            "people": {
                "head": {
                    "age": {year: 40 for year in years},
                    "health_insurance_premiums": {year: 3_000 for year in years},
                }
            },
            "tax_units": {
                "tax_unit": {
                    "members": ["head"],
                    "adjusted_gross_income": {year: 30_000 for year in years},
                    "medical_expense_deduction": {2026: 3_000},
                }
            },
            "households": {
                "household": {
                    "members": ["head"],
                    "state_code": {year: "ID" for year in years},
                }
            },
        },
    )
    # Create branches before calculating the helper so they inherit no
    # previously calculated Idaho value. A sibling's input must not change
    # the parent's derived claim, but a nested branch inherits that input.
    actual_claim = simulation.get_branch("actual_claim")
    actual_claim.set_input("medical_expense_deduction", 2025, np.array([3_000]))
    nested_claim = actual_claim.get_branch("nested_claim")
    deleted_claim = simulation.get_branch("deleted_claim")
    deleted_claim.set_input("medical_expense_deduction", 2025, np.array([3_000]))
    deleted_claim.delete_arrays("medical_expense_deduction", 2025)

    variable = "id_health_insurance_premiums_medical_deduction"
    assert simulation.calculate(variable, 2025).tolist() == [750]
    assert simulation.calculate(variable, 2026).tolist() == [3_000]
    assert actual_claim.calculate(variable, 2025).tolist() == [3_000]
    assert nested_claim.calculate(variable, 2025).tolist() == [3_000]
    # Check before federal recalculation, while the deleted input's array is
    # absent. Core versions before 3.32.27 retain its input key, so recalculating
    # first triggers the provenance defect documented in the PR's limitation.
    assert deleted_claim.calculate(variable, 2025).tolist() == [750]


@pytest.mark.xfail(
    condition=Version(version("policyengine-core")) < Version("3.32.27"),
    strict=True,
    reason=(
        "policyengine-core<3.32.27 retains deleted input provenance and "
        "misclassifies a federal medical deduction recalculated before the "
        "Idaho helper as supplied; fixed by policyengine-core#561."
    ),
)
def test_deleted_medical_input_recalculated_federal_first():
    year = 2025
    simulation = Simulation(
        tax_benefit_system=SYSTEM,
        situation={
            "people": {
                "head": {
                    "age": {year: 40},
                    "is_tax_unit_head": {year: True},
                    "health_insurance_premiums": {year: 3_000},
                },
                "dependent": {
                    "age": {year: 20},
                    "is_tax_unit_dependent": {year: True},
                    "health_insurance_premiums": {year: 500},
                },
            },
            "tax_units": {
                "tax_unit": {
                    "members": ["head", "dependent"],
                    "adjusted_gross_income": {year: 30_000},
                    "standard_deduction": {year: 15_750},
                    "id_itemized_deductions": {year: 20_000},
                }
            },
            "households": {
                "household": {
                    "members": ["head", "dependent"],
                    "state_code": {year: "ID"},
                }
            },
        },
    )
    simulation.set_input("medical_expense_deduction", year, np.array([3_000]))
    simulation.delete_arrays("medical_expense_deduction", year)

    # Federal first: 3,000 + 500 - 30,000 * 7.5% = 1,250.
    assert simulation.calculate("medical_expense_deduction", year).tolist() == [1_250]
    # Idaho excludes the dependent's payment: medical overlap is
    # 3,000 - 30,000 * 7.5% = 750, leaving 3,000 - 750 = 2,250.
    # Core's provenance defect before 3.32.27 uses 1,250 and returns 1,750.
    assert simulation.calculate(
        "id_health_insurance_premiums_subtraction", year
    ).tolist() == [2_250]
