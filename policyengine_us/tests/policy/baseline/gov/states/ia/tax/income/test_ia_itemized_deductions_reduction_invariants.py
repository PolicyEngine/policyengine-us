"""Invariants of Iowa's 2018 limitation on itemized deductions.

The 2018 IA 104 worksheet limits the 2018 IA Schedule A total of a filer whose
federal adjusted gross income exceeds the applicable amount for the federal
filing status (line 8):
https://revenue.iowa.gov/media/2335/download?inline=#page=1
Line 11 is the smaller of 80% of the deductions subject to the limitation
(line 6) and 3% of the excess income (line 10). Lines 12 to 21 then remove
the Iowa income tax on federal Schedule A line 5a in proportion, as
701 IAC 41.11(1) does, at a share that line 18 enters to the nearest tenth of
a percent:
https://www.legis.iowa.gov/docs/iac/chapter/03-28-2018.701.41.pdf#page=10

So each bound below allows ROUNDING of the Iowa income tax on line 2, the most
that line 18's rounding moves line 21 from the exact share.

Hypothesis draws deduction inputs, Iowa income tax, sales tax and federal AGI
relative to the applicable amount, so every filing status gets limited cases.
Each draw becomes one simulation with four tax units per case: the drawn
case; the case without miscellaneous expenses ("fixed"), whose Schedule A
total does not depend on AGI; "fixed" with higher AGI; and "fixed" with more
Iowa income tax. For every tax unit:

1. Accounting: ia_itemized_deductions_unit is the pre-limitation total minus
   the reduction, because Schedule A line 26 takes IA 104 line 21.
2. Never raises: apart from rounding, the reduction is never negative, so
   the limitation never raises the deduction, because line 11 is the smaller
   of two nonnegative amounts and the exact share is at most 100%.
3. Bounded: apart from rounding, the reduction is at most 80% of the
   deductions other than medical expenses and investment interest, because
   line 6 caps line 11 at 80% of line 5 and Schedule A bears only its line-1
   share of line 11.
4. Threshold: no reduction when federal AGI is at most the applicable
   amount, because line 9 then stops the worksheet.
5. Monotone in AGI: with the deductions fixed, higher AGI never lowers the
   reduction, because line 9 grows with line 7.
6. Monotone in Iowa income tax: more Iowa income tax never raises the
   reduction, because lines 15 to 20 give the Iowa income tax its share of
   line 11.
7. Worksheet: the reduction stays within rounding of line 11 times the
   Schedule A share, (line 1 - line 4) / line 5, with line 1 and AGI taken
   from the model and lines 2 to 11 restated here from the draw.

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
# 2018 IA 104 line 10.
AGI_RATE = 0.03
# 2018 IA 104 line 18 rounds to a tenth of a percent, half of which is 0.05%.
ROUNDING = 0.0005
TOLERANCE = 0.1
VARIANTS = ("drawn", "fixed", "higher_agi", "more_iowa_tax")

amount = st.integers(min_value=0, max_value=60_000)
case_strategy = st.fixed_dictionaries(
    {
        "filing_status": st.sampled_from(sorted(APPLICABLE_AMOUNT)),
        "agi_offset": st.integers(min_value=-50_000, max_value=1_000_000),
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


def base_agi(case):
    return max(0, APPLICABLE_AMOUNT[case["filing_status"]] + case["agi_offset"])


def line_2(case, variant):
    """Iowa income tax on federal Schedule A line 5a, as the draw sets it."""
    iowa_income_tax = case["iowa_income_tax"]
    if variant == "more_iowa_tax":
        iowa_income_tax += case["iowa_income_tax_increase"]
    return iowa_income_tax if iowa_income_tax >= case["sales_tax"] else 0


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
            agi = base_agi(case)
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
        applicable_amount = APPLICABLE_AMOUNT[case["filing_status"]]
        for j, variant in enumerate(VARIANTS):
            context = (variant, case)
            # Line 2 and the most that rounding moves the result.
            iowa_tax = line_2(case, variant)
            rounding = ROUNDING * iowa_tax
            # 1. Accounting.
            assert unit[i, j] == pytest.approx(
                pre[i, j] - reduction[i, j], abs=TOLERANCE
            ), context
            # 2. Never raises, apart from rounding.
            assert reduction[i, j] >= -rounding - TOLERANCE, context
            assert unit[i, j] <= pre[i, j] + rounding + TOLERANCE, context
            # 3. Bounded by line 6, apart from rounding.
            assert (
                reduction[i, j]
                <= CAP_RATE * max(0, pre[i, j] - excluded) + rounding + TOLERANCE
            ), context
            # 4. Threshold.
            if agi[i, j] <= applicable_amount:
                assert reduction[i, j] == 0, context
            # 7. Worksheet: lines 3, 5, 6, 9, 10 and 11, then the exact share.
            line_5 = max(0, pre[i, j] + iowa_tax - excluded)
            line_11 = min(
                CAP_RATE * line_5, AGI_RATE * max(0, agi[i, j] - applicable_amount)
            )
            exact = line_11 * max(0, pre[i, j] - excluded) / line_5 if line_5 else 0
            assert reduction[i, j] == pytest.approx(exact, abs=rounding + TOLERANCE), (
                context
            )
        # The fixed variants share one Schedule A total.
        assert pre[i, higher_agi] == pytest.approx(pre[i, fixed], abs=TOLERANCE), case
        assert pre[i, more_iowa_tax] == pytest.approx(pre[i, fixed], abs=TOLERANCE), (
            case
        )
        # 5. Monotone in AGI, apart from rounding at each of the two points.
        fixed_rounding = ROUNDING * line_2(case, "fixed")
        assert (
            reduction[i, higher_agi]
            >= reduction[i, fixed] - 2 * fixed_rounding - TOLERANCE
        ), case
        # 6. Monotone in Iowa income tax, apart from rounding at each point.
        more_rounding = ROUNDING * line_2(case, "more_iowa_tax")
        assert (
            reduction[i, more_iowa_tax]
            <= reduction[i, fixed] + fixed_rounding + more_rounding + TOLERANCE
        ), case
