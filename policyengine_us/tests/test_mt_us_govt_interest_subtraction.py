"""Invariants of Montana's subtraction for US government interest from 2024.

MCA 15-30-2120(3)(b)(i) subtracts "interest from obligations of the United
States government and exempt-interest dividends attributable to that
interest" from federal taxable income:
https://mca.legmt.gov/bills/mca/title_0150/chapter_0300/part_0210/section_0200/0150-0300-0210-0200.html
The 2024 Form 2 reports it on Schedule I, Part I, line 11 (instructions PDF
page 25) and the 2025 Form 2 on line 9 (instructions PDF page 23). Line 7
(Montana taxable income) cannot fall below zero.

Each generated household runs twice in one simulation: once with
us_govt_interest_person = u on the bondholder and once with 0. Only that
classification input differs, so federal income and deductions match across
the pair. For every household and each year from 2024 to 2026:

1. Accounting: Montana taxable income falls by exactly min(u_eff, TI_0),
   where TI_0 is Montana taxable income without the subtraction. u_eff = u
   when the head or spouse holds the bonds and 0 when a dependent does.
   The dependent case is intended: irs_gross_income zeroes every income
   source of a tax-unit dependent, so a dependent's interest never enters
   the return, and the return subtracts none of it.
2. Monotone: Montana income tax does not rise with the subtraction.
3. Bound: Montana taxable income is nonnegative.

Taxable income is integral here (integer inputs and deductions), so float32
represents it exactly; tax comparisons allow one cent.
"""

import hypothesis
import hypothesis.strategies as st
import numpy as np

from policyengine_us import Simulation

YEARS = (2024, 2025, 2026)
AMOUNT_TOLERANCE = 0.01
SLOW = [hypothesis.HealthCheck.too_slow, hypothesis.HealthCheck.data_too_large]


def bondholder(case):
    # A single filer has no spouse; put the spouse's bonds on the head.
    if case["holder"] == "spouse" and not case["joint"]:
        return "head"
    return case["holder"]


def us_interest(case):
    return round(case["interest"] * case["us_share"])


def build_situation(cases):
    people, tax_units, marital_units, households = {}, {}, {}, {}

    def by_year(value):
        return {year: value for year in YEARS}

    for i, case in enumerate(cases):
        holder = bondholder(case)
        for variant, amount in (("with", us_interest(case)), ("without", 0)):
            key = f"{variant}_{i}"
            head, spouse, dependent = (
                f"head_{key}",
                f"spouse_{key}",
                f"dependent_{key}",
            )
            filers = [head, spouse] if case["joint"] else [head]
            # Only a dependent bondholder joins the unit; a single filer with
            # a dependent child files as head of household.
            members = filers + ([dependent] if holder == "dependent" else [])
            people[head] = {
                "age": by_year(case["age"]),
                "employment_income": by_year(case["wages"]),
                "home_mortgage_interest": by_year(case["mortgage"]),
            }
            if case["joint"]:
                people[spouse] = {"age": by_year(case["age"])}
            if holder == "dependent":
                people[dependent] = {
                    "age": by_year(10),
                    "is_tax_unit_dependent": by_year(True),
                }
            owner = {"head": head, "spouse": spouse, "dependent": dependent}[holder]
            people[owner]["taxable_interest_income"] = by_year(case["interest"])
            people[owner]["us_govt_interest_person"] = by_year(amount)
            tax_units[f"tax_unit_{key}"] = {
                "members": members,
                "state_withheld_income_tax": by_year(case["state_income_tax"]),
                "state_sales_tax": by_year(0),
                "local_sales_tax": by_year(0),
                "local_income_tax": by_year(0),
            }
            marital_units[f"marital_unit_{key}"] = {"members": filers}
            if holder == "dependent":
                marital_units[f"dependent_marital_unit_{key}"] = {
                    "members": [dependent]
                }
            households[f"household_{key}"] = {
                "members": members,
                "state_code": by_year("MT"),
            }
    return {
        "people": people,
        "tax_units": tax_units,
        "marital_units": marital_units,
        "households": households,
    }


def calculate(cases):
    """Return {year: (taxable income, tax)}, each shaped [case, with/without]."""
    simulation = Simulation(situation=build_situation(cases))
    results = {}
    for year in YEARS:
        taxable_income = np.asarray(
            simulation.calculate("mt_taxable_income", year)
        ).reshape(len(cases), 2)
        tax = np.asarray(simulation.calculate("mt_income_tax", year)).reshape(
            len(cases), 2
        )
        results[year] = taxable_income, tax
    return results


def assert_properties(cases):
    for year, (taxable_income, tax) in calculate(cases).items():
        for i, case in enumerate(cases):
            u_eff = 0 if bondholder(case) == "dependent" else us_interest(case)
            ti_with, ti_without = taxable_income[i]
            context = (year, case, taxable_income[i], tax[i])
            assert ti_with >= 0 and ti_without >= 0, context
            assert ti_without - ti_with == min(u_eff, ti_without), context
            assert tax[i][0] <= tax[i][1] + AMOUNT_TOLERANCE, context


def case(joint, holder, wages, interest, us_share, **kwargs):
    return {
        "joint": joint,
        "holder": holder,
        "wages": wages,
        "interest": interest,
        "us_share": us_share,
        "state_income_tax": kwargs.get("state_income_tax", 0),
        "mortgage": kwargs.get("mortgage", 0),
        "age": kwargs.get("age", 40),
    }


# The subtraction exceeds taxable income before it (the zero floor binds),
# a dependent holds the bonds, and interior cuts, single and joint.
PINNED = [
    case(False, "head", 0, 30_000, 1.0),
    case(True, "spouse", 5_000, 30_000, 1.0, age=70),
    case(False, "dependent", 40_000, 10_000, 1.0),
    case(
        True, "dependent", 80_000, 10_000, 1.0, state_income_tax=4_000, mortgage=30_000
    ),
    case(False, "head", 60_000, 5_000, 0.5),
    case(True, "spouse", 120_000, 8_000, 0.75, state_income_tax=9_000, mortgage=30_000),
    case(
        False,
        "head",
        200_000,
        30_000,
        1.0,
        state_income_tax=15_000,
        mortgage=30_000,
        age=70,
    ),
]


def test_worked_subtractions():
    # 2024 single, 10,000 wages and 10,000 Treasury interest: Form 2 line 3 is
    # 20,000 - 14,600 = 5,400, so the 10,000 subtraction stops at zero.
    # 2025 joint, spouse holds 3,000 of bonds: 83,000 - 31,500 - 3,000 = 48,500.
    # A dependent's 10,000 of bonds leaves the return unchanged; the parent
    # files as head of household (2024 standard deduction 21,900).
    cases = [
        case(False, "head", 10_000, 10_000, 1.0),
        case(True, "spouse", 80_000, 3_000, 1.0),
        case(False, "dependent", 40_000, 10_000, 1.0),
    ]
    results = calculate(cases)
    taxable_income_2024 = results[2024][0]
    taxable_income_2025 = results[2025][0]
    assert taxable_income_2024[0].tolist() == [0, 5_400]
    assert taxable_income_2025[1].tolist() == [48_500, 51_500]
    assert taxable_income_2024[2].tolist() == [40_000 - 21_900] * 2


@hypothesis.settings(
    max_examples=10,
    deadline=None,
    derandomize=True,
    suppress_health_check=SLOW,
)
@hypothesis.example(PINNED)
@hypothesis.given(
    st.lists(
        st.fixed_dictionaries(
            {
                "joint": st.booleans(),
                "holder": st.sampled_from(["head", "spouse", "dependent"]),
                "wages": st.one_of(
                    st.integers(min_value=0, max_value=20_000),
                    st.integers(min_value=0, max_value=250_000),
                ),
                "interest": st.integers(min_value=0, max_value=30_000),
                "us_share": st.one_of(st.just(1.0), st.floats(0, 1)),
                "state_income_tax": st.integers(min_value=0, max_value=15_000),
                "mortgage": st.sampled_from([0, 12_000, 30_000]),
                "age": st.sampled_from([40, 70]),
            }
        ),
        min_size=1,
        max_size=6,
    )
)
def test_subtraction_properties(cases):
    assert_properties(cases)
