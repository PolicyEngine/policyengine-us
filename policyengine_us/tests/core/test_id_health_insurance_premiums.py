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
                    # The federal subtotal and Idaho's claimant worksheet
                    # both count a dependent's other costs.
                    "other_medical_expenses": {year: 500},
                },
            },
            "tax_units": {
                "tax_unit": {
                    "members": ["head", "dependent"],
                    "adjusted_gross_income": {year: 30_000},
                    "standard_deduction": {year: 15_750},
                    "id_itemized_deductions": {year: 20_000},
                    # From derived inputs the claimant worksheet equals the
                    # federal deduction. A supplied Idaho premium amount below
                    # the 3,000 Schedule A premiums keeps the two apart.
                    "id_qualified_health_insurance_premiums": {year: 2_000},
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
    # Idaho's claimant overlap is 2,000 + 500 - 30,000 * 7.5% = 250, leaving
    # 2,000 - 250 = 1,750. Core's provenance defect before 3.32.27 uses the
    # 1,250 federal deduction and returns 2,000 - 1,250 = 750.
    assert simulation.calculate(
        "id_health_insurance_premiums_subtraction", year
    ).tolist() == [1_750]


# Form 39R worksheet lines 1-6 take the medical expenses claimed on federal
# Schedule A, which counts bills the filers paid for dependents. Premium inputs
# sit on the payer and other medical expenses on the person cared for, so the
# claimant worksheet counts the filers' premiums and every member's other
# costs. Each drawn return runs in one vectorized simulation per year with
# these variants:
VARIANTS = (
    "drawn",
    # every member's other costs recorded on the head;
    "bills_on_head",
    # every member's other costs recorded on one dependent;
    "bills_on_dependent",
    # one dependent's other costs raised;
    "dependent_bills_raised",
    # every dependent's own premiums set to 0.
    "no_dependent_premiums",
)
# The drawn high incomes reach the 2026 itemized limitation (IRC 68).
CLAIMANT_YEARS = (2025, 2026)
IDAHO_OUTPUTS = (
    "id_health_insurance_premiums_medical_deduction",
    "id_qualified_health_insurance_premiums",
    "id_itemized_deductions",
    "id_itemizes",
    "id_health_insurance_premiums_subtraction",
    "id_deductions",
)
CENT = 0.01


@st.composite
def claimant_returns(draw):
    filers = draw(st.sampled_from([1, 2]))
    dependents = draw(st.integers(1, 2))
    members = filers + dependents
    return {
        "filers": filers,
        "premiums": [draw(st.integers(0, 20_000)) for _ in range(members)],
        "other": [draw(st.integers(0, 40_000)) for _ in range(members)],
        "agi": draw(st.integers(0, 150_000) | st.integers(600_000, 900_000)),
        "interest": draw(st.integers(0, 40_000)),
        "above_line": draw(st.integers(0, 25_000)),
        "receiver": filers + draw(st.integers(0, dependents - 1)),
        "raise": draw(st.integers(1, 10_000)),
    }


def _claimant_inputs(case, variant):
    premiums = list(case["premiums"])
    other = list(case["other"])
    if variant == "bills_on_head":
        other = [sum(other)] + [0] * (len(other) - 1)
    elif variant == "bills_on_dependent":
        moved = [0] * len(other)
        moved[case["receiver"]] = sum(other)
        other = moved
    elif variant == "dependent_bills_raised":
        other[case["receiver"]] += case["raise"]
    elif variant == "no_dependent_premiums":
        premiums[case["filers"] :] = [0] * (len(premiums) - case["filers"])
    return premiums, other


def _claimant_simulation(cases, year):
    people, tax_units, households, rows = {}, {}, {}, []
    for index, case in enumerate(cases):
        for variant in VARIANTS:
            unit = f"case_{index}_{variant}"
            premiums, other = _claimant_inputs(case, variant)
            members = [f"{unit}_{member}" for member in range(len(premiums))]
            for member, person in enumerate(members):
                filer = member < case["filers"]
                people[person] = {
                    "age": {year: 40 if filer else 10},
                    "is_tax_unit_head": {year: member == 0},
                    "is_tax_unit_spouse": {year: member == 1 and filer},
                    "is_tax_unit_dependent": {year: not filer},
                    "health_insurance_premiums": {year: premiums[member]},
                    "other_medical_expenses": {year: other[member]},
                }
            tax_units[unit] = {
                "members": members,
                "adjusted_gross_income": {year: case["agi"]},
                "self_employed_health_insurance_ald": {year: case["above_line"]},
                "interest_deduction": {year: case["interest"]},
                "salt_deduction": {year: 0},
                "id_salt_deduction": {year: 0},
            }
            households[unit] = {"members": members, "state_code": {year: "ID"}}
            rows.append((index, variant))
    simulation = Simulation(
        tax_benefit_system=SYSTEM,
        situation={
            "people": people,
            "tax_units": tax_units,
            "households": households,
        },
    )
    return simulation, rows


@settings(max_examples=8, deadline=None, derandomize=True)
@given(cases=st.lists(claimant_returns(), min_size=2, max_size=3))
def test_claimant_worksheet_counts_bills_paid_for_dependents(cases):
    for year in CLAIMANT_YEARS:
        simulation, rows = _claimant_simulation(cases, year)
        floor = SYSTEM.parameters(year).gov.irs.deductions.itemized.medical.floor
        values = {
            # id_itemizes compares as 0 or 1.
            variable: dict(
                zip(rows, simulation.calculate(variable, year).astype(float))
            )
            for variable in IDAHO_OUTPUTS
            + ("medical_expense_deduction", "itemized_taxable_income_deductions")
        }
        for index, case in enumerate(cases):

            def value(variable, variant="drawn"):
                return values[variable][(index, variant)]

            worksheet = value("id_health_insurance_premiums_medical_deduction")
            # 1. Differential: an independent oracle, the federal Schedule A
            # deduction, and Idaho's worksheet agree.
            filer_premiums = sum(case["premiums"][: case["filers"]])
            oracle = max(
                0,
                max(0, filer_premiums - case["above_line"])
                + sum(case["other"])
                - floor * max(0, case["agi"]),
            )
            assert worksheet == pytest.approx(oracle, abs=CENT), case
            assert value("medical_expense_deduction") == pytest.approx(
                worksheet, abs=CENT
            ), case
            # 2. Idaho's medical correction leaves a derived federal itemized
            # total unchanged: the two medical deductions agree.
            assert value("id_itemized_deductions") == pytest.approx(
                value("itemized_taxable_income_deductions"), abs=CENT
            ), case
            # 3. Relocation: whose input records a bill changes no Idaho
            # amount, and neither do a dependent's own premiums.
            for variant in (
                "bills_on_head",
                "bills_on_dependent",
                "no_dependent_premiums",
            ):
                for variable in IDAHO_OUTPUTS:
                    assert value(variable, variant) == pytest.approx(
                        value(variable), abs=CENT
                    ), (variable, variant, case)
            # 4. Monotonicity: more bills for a dependent never lower the
            # worksheet.
            assert (
                value(
                    "id_health_insurance_premiums_medical_deduction",
                    "dependent_bills_raised",
                )
                >= worksheet - CENT
            ), case
            # 5. Bounds: the subtraction stays within the qualified premiums.
            assert (
                -CENT
                <= value("id_health_insurance_premiums_subtraction")
                <= value("id_qualified_health_insurance_premiums") + CENT
            ), case
