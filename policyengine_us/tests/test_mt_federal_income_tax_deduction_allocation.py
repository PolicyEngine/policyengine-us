"""Invariants of Montana's separate-spouse federal tax allocation.

The 2022 Form 2 instructions, Itemized Deductions Schedule line 4a (PDF
page 33), attribute federal withholding to the spouse earning the income;
line 4 limits each separately filing spouse's deduction to $5,000:
https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2022_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=33

The model's positive federal-AGI shares approximate spouse-specific payments
because withholding inputs are unavailable. The form does not prescribe an
allocation when neither filer has positive income; the model retains main's
zero allocation in that case rather than inventing a head-only fallback. For
every eligible tax unit, the method must:

1. With positive filer AGI, allocate all of the couple's federal tax across
   head and spouse before each spouse's cap, without any dependent share.
2. Treat negative filer AGI identically to zero AGI and disregard changes
   to dependent AGI.
3. Allocate no tax when neither filer has positive AGI, as main does when
   its allocation denominator is nonpositive.
4. Keep deductions nonnegative and at most $5,000 per person; conserve
   nonnegative federal tax when filer AGI is positive and federal tax is at
   most $5,000, so no cap can bind.

Each generated case is simulated alongside clipped-income, changed-dependent,
and zero-filer-income variants. Comparisons allow one cent for float32 tax
amounts and eight float32 spacings for dimensionless shares.
"""

import hypothesis
import hypothesis.strategies as st
import numpy as np
import pytest

from policyengine_us import Simulation

YEAR = 2022
CAP = 5_000
SHARE_TOLERANCE = 8 * np.finfo(np.float32).eps
AMOUNT_TOLERANCE = 0.01
ARRANGEMENTS = ("original", "clipped", "dependent", "zero")


def build_situation(cases):
    people, tax_units, households = {}, {}, {}
    for i, case in enumerate(cases):
        for arrangement in ARRANGEMENTS:
            key = f"{arrangement}_{i}"
            head, spouse, dependent = (
                f"head_{key}",
                f"spouse_{key}",
                f"dependent_{key}",
            )
            filer_incomes = [case["head_agi"], case["spouse_agi"]]
            if arrangement == "clipped":
                filer_incomes = [max(income, 0) for income in filer_incomes]
            elif arrangement == "zero":
                filer_incomes = [0, 0]
            dependent_income = case["dependent_agi"]
            if arrangement in ("dependent", "zero"):
                dependent_income = abs(dependent_income) + 25_000
            for name, age, income, is_dependent in zip(
                (head, spouse, dependent),
                (50, 49, 16),
                (*filer_incomes, dependent_income),
                (False, False, True),
            ):
                people[name] = {
                    "age": {YEAR: age},
                    "adjusted_gross_income_person": {YEAR: income},
                    "is_tax_unit_dependent": {YEAR: is_dependent},
                }
            tax_units[f"tax_unit_{key}"] = {
                "members": [head, spouse, dependent],
                "income_tax_before_refundable_credits": {YEAR: case["federal_tax"]},
                "state_filing_status_if_married_filing_separately_on_same_return": {
                    YEAR: "SEPARATE"
                },
            }
            households[f"household_{key}"] = {
                "members": [head, spouse, dependent],
                "state_code": {YEAR: "MT"},
            }
    return {"people": people, "tax_units": tax_units, "households": households}


def calculate(cases):
    simulation = Simulation(situation=build_situation(cases))
    shape = (len(cases), len(ARRANGEMENTS), 3)
    shares = np.asarray(
        simulation.calculate("mt_federal_income_tax_deduction_share", YEAR)
    ).reshape(shape)
    deductions = np.asarray(
        simulation.calculate("mt_federal_income_tax_deduction_indiv", YEAR)
    ).reshape(shape)
    return shares, deductions


def assert_properties(cases):
    shares, deductions = calculate(cases)
    for i, case in enumerate(cases):
        case_shares, case_deductions = shares[i], deductions[i]
        # Each array is indexed [arrangement, head/spouse/dependent].
        has_positive_filer_income = case["head_agi"] > 0 or case["spouse_agi"] > 0
        assert np.all(case_shares >= 0), case
        assert np.all(case_shares <= 1), case
        assert case_shares.sum(axis=1) == pytest.approx(
            [int(has_positive_filer_income)] * 3 + [0], abs=SHARE_TOLERANCE
        ), case
        assert np.all(case_shares[:, 2] == 0), case
        # Negative income and dependent income cannot shift tax to or away
        # from either filer.
        for arrangement in (1, 2):
            assert case_shares[arrangement] == pytest.approx(
                case_shares[0], abs=SHARE_TOLERANCE
            ), case
            assert case_deductions[arrangement] == pytest.approx(
                case_deductions[0], abs=AMOUNT_TOLERANCE
            ), case
        # The source is silent on zero filer income; preserve main's zero
        # allocation, even with a positive-income dependent.
        assert case_shares[3] == pytest.approx([0, 0, 0], abs=SHARE_TOLERANCE), case
        federal_tax = max(case["federal_tax"], 0)
        assert case_deductions[3] == pytest.approx([0, 0, 0], abs=AMOUNT_TOLERANCE), (
            case
        )
        assert np.all(case_deductions >= 0), case
        assert np.all(case_deductions <= CAP), case
        assert np.all(case_deductions[:, 2] == 0), case
        if not has_positive_filer_income:
            assert np.all(case_deductions == 0), case
        elif federal_tax <= CAP:
            assert case_deductions[:3].sum(axis=1) == pytest.approx(
                [federal_tax] * 3, abs=AMOUNT_TOLERANCE
            ), case


def test_worked_allocations():
    cases = [
        # 2_000 * 40_000 / (40_000 + 0) = 2_000; the dependent's
        # 10_000 is excluded. An unmasked allocator gives 1_600 / 0 / 400.
        {
            "head_agi": 40_000,
            "spouse_agi": 0,
            "dependent_agi": 10_000,
            "federal_tax": 2_000,
        },
        # Negative head AGI contributes zero; all 2_000 goes to the spouse.
        {
            "head_agi": -5_000,
            "spouse_agi": 10_000,
            "dependent_agi": 25_000,
            "federal_tax": 2_000,
        },
        # Neither filer has positive AGI: main's zero allocation is retained.
        {
            "head_agi": 0,
            "spouse_agi": 0,
            "dependent_agi": 10_000,
            "federal_tax": 2_000,
        },
        {
            "head_agi": -5_000,
            "spouse_agi": -2_000,
            "dependent_agi": 10_000,
            "federal_tax": 2_000,
        },
    ]
    shares, deductions = calculate(cases)
    assert shares[:, 0] == pytest.approx(
        np.array([[1, 0, 0], [0, 1, 0], [0, 0, 0], [0, 0, 0]]),
        abs=SHARE_TOLERANCE,
    )
    assert deductions[:, 0] == pytest.approx(
        np.array([[2_000, 0, 0], [0, 2_000, 0], [0, 0, 0], [0, 0, 0]]),
        abs=AMOUNT_TOLERANCE,
    )


@hypothesis.settings(
    max_examples=10,
    deadline=None,
    suppress_health_check=[hypothesis.HealthCheck.too_slow],
)
@hypothesis.given(
    st.lists(
        st.fixed_dictionaries(
            {
                "head_agi": st.integers(min_value=-100_000, max_value=100_000),
                "spouse_agi": st.integers(min_value=-100_000, max_value=100_000),
                "dependent_agi": st.integers(min_value=-100_000, max_value=100_000),
                "federal_tax": st.integers(min_value=-5_000, max_value=30_000),
            }
        ),
        min_size=1,
        max_size=6,
    )
)
def test_allocation_properties(cases):
    assert_properties(cases)
