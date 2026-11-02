"""Invariants of Iowa's 2018 limitation on itemized deductions.

The 2018 IA 104 worksheet limits the 2018 IA Schedule A total of a filer whose
federal adjusted gross income exceeds the applicable amount for the federal
filing status (line 8):
https://revenue.iowa.gov/media/2335/download?inline=#page=1
Line 11 is the smaller of 80% of the deductions subject to the limitation
(line 6) and 3% of the excess income (line 10). Lines 12 to 21 then remove
the Iowa income tax on federal Schedule A line 5a in proportion, as
701 IAC 41.11(1) does:
https://www.legis.iowa.gov/docs/iac/chapter/03-28-2018.701.41.pdf#page=10

Hypothesis draws deduction inputs, Iowa income tax, sales tax and federal
AGI. Each draw becomes one simulation with four tax units per case: the drawn
case; the case without miscellaneous expenses ("fixed"), whose Schedule A
total does not depend on AGI; "fixed" with higher AGI; and "fixed" with more
Iowa income tax. For every tax unit:

1. Accounting: ia_itemized_deductions_unit is the pre-limitation total minus
   the reduction, because Schedule A line 26 takes IA 104 line 21.
2. Never raises: the reduction is never negative, so the limitation never
   raises the deduction, because line 11 is the smaller of two nonnegative
   amounts and line 18 is at most 100%.
3. Bounded: the reduction is at most 80% of the deductions other than
   medical expenses and investment interest, because line 6 caps line 11 at
   80% of line 5 and Schedule A bears only its line-1 share of line 11.
4. Threshold: no reduction when federal AGI is at most the applicable
   amount, because line 9 then stops the worksheet.
5. Monotone in AGI: with the deductions fixed, higher AGI never lowers the
   reduction, because line 9 grows with line 7.
6. Monotone in Iowa income tax: more Iowa income tax never raises the
   reduction, because lines 15 to 20 give the Iowa income tax its share of
   line 11.

Comparisons allow ten cents: float32 spacing is under seven cents below
$1 million.
"""

import hypothesis
import hypothesis.strategies as st
import numpy as np
import pytest

from policyengine_us import Simulation

YEAR = 2018
# 2018 IA 104 line 8, by federal filing status.
APPLICABLE_AMOUNT = {
    "SINGLE": 266_700,
    "JOINT": 320_000,
    "SEPARATE": 160_000,
    "HEAD_OF_HOUSEHOLD": 293_350,
    "SURVIVING_SPOUSE": 320_000,
}
# 2018 IA 104 line 6.
CAP_RATE = 0.8
TOLERANCE = 0.1
VARIANTS = ("drawn", "fixed", "higher_agi", "more_iowa_tax")

amount = st.integers(min_value=0, max_value=60_000)
case_strategy = st.fixed_dictionaries(
    {
        "filing_status": st.sampled_from(sorted(APPLICABLE_AMOUNT)),
        "agi": st.integers(min_value=0, max_value=1_500_000),
        "agi_increase": st.integers(min_value=0, max_value=500_000),
        "real_estate_taxes": amount,
        "mortgage_interest": amount,
        "charity": amount,
        "medical": amount,
        "investment_interest": amount,
        "misc_expenses": amount,
        "iowa_income_tax": st.integers(min_value=0, max_value=120_000),
        "iowa_income_tax_increase": st.integers(min_value=0, max_value=60_000),
        "sales_tax": amount,
    }
)


def build_situation(cases):
    people, tax_units, households = {}, {}, {}
    for i, case in enumerate(cases):
        for variant in VARIANTS:
            key = f"{variant}_{i}"
            person = f"person_{key}"
            misc_expenses = case["misc_expenses"] if variant == "drawn" else 0
            iowa_income_tax = case["iowa_income_tax"]
            if variant == "more_iowa_tax":
                iowa_income_tax += case["iowa_income_tax_increase"]
            agi = case["agi"]
            if variant == "higher_agi":
                agi += case["agi_increase"]
            people[person] = {
                "age": {YEAR: 45},
                "real_estate_taxes": {YEAR: case["real_estate_taxes"]},
                "deductible_mortgage_interest": {YEAR: case["mortgage_interest"]},
                "investment_interest_expense": {YEAR: case["investment_interest"]},
                "unreimbursed_business_employee_expenses": {YEAR: misc_expenses},
                "ia_withheld_income_tax": {YEAR: iowa_income_tax},
            }
            tax_units[f"tax_unit_{key}"] = {
                "members": [person],
                "filing_status": {YEAR: case["filing_status"]},
                "adjusted_gross_income": {YEAR: agi},
                "charitable_deduction": {YEAR: case["charity"]},
                "medical_expense_deduction": {YEAR: case["medical"]},
                "state_sales_tax": {YEAR: case["sales_tax"]},
                "local_sales_tax": {YEAR: 0},
            }
            households[f"household_{key}"] = {
                "members": [person],
                "state_code": {YEAR: "IA"},
            }
    return {"people": people, "tax_units": tax_units, "households": households}


def calculate(cases):
    simulation = Simulation(situation=build_situation(cases))
    shape = (len(cases), len(VARIANTS))
    return {
        name: np.asarray(simulation.calculate(name, YEAR)).reshape(shape)
        for name in (
            "adjusted_gross_income",
            "ia_itemized_deductions_pre_limitation",
            "ia_itemized_deductions_reduction",
            "ia_itemized_deductions_unit",
        )
    }


@hypothesis.settings(
    max_examples=20,
    deadline=None,
    derandomize=True,
    suppress_health_check=[hypothesis.HealthCheck.too_slow],
)
@hypothesis.given(st.lists(case_strategy, min_size=1, max_size=8))
def test_ia_itemized_deductions_reduction_invariants(cases):
    values = calculate(cases)
    agi = values["adjusted_gross_income"]
    pre = values["ia_itemized_deductions_pre_limitation"]
    reduction = values["ia_itemized_deductions_reduction"]
    unit = values["ia_itemized_deductions_unit"]
    fixed, higher_agi, more_iowa_tax = (
        VARIANTS.index(variant) for variant in ("fixed", "higher_agi", "more_iowa_tax")
    )
    for i, case in enumerate(cases):
        excluded = case["medical"] + case["investment_interest"]
        for j, variant in enumerate(VARIANTS):
            context = (variant, case)
            # 1. Accounting.
            assert unit[i, j] == pytest.approx(
                pre[i, j] - reduction[i, j], abs=TOLERANCE
            ), context
            # 2. Never raises.
            assert reduction[i, j] >= 0, context
            assert unit[i, j] <= pre[i, j] + TOLERANCE, context
            # 3. Bounded by line 6.
            assert (
                reduction[i, j] <= CAP_RATE * max(0, pre[i, j] - excluded) + TOLERANCE
            ), context
            # 4. Threshold.
            if agi[i, j] <= APPLICABLE_AMOUNT[case["filing_status"]]:
                assert reduction[i, j] == 0, context
        # The fixed variants share one Schedule A total.
        assert pre[i, higher_agi] == pytest.approx(pre[i, fixed], abs=TOLERANCE), case
        assert pre[i, more_iowa_tax] == pytest.approx(pre[i, fixed], abs=TOLERANCE), (
            case
        )
        # 5. Monotone in AGI.
        assert reduction[i, higher_agi] >= reduction[i, fixed] - TOLERANCE, case
        # 6. Monotone in Iowa income tax.
        assert reduction[i, more_iowa_tax] <= reduction[i, fixed] + TOLERANCE, case
