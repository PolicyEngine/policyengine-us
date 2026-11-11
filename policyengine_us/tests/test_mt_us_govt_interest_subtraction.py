"""Invariants of Montana's subtraction for US government interest from 2024.

MCA 15-30-2120(3)(b)(i) subtracts "interest from obligations of the United
States government and exempt-interest dividends attributable to that
interest" from federal taxable income:
https://mca.legmt.gov/bills/mca/title_0150/chapter_0300/part_0210/section_0200/0150-0300-0210-0200.html
The 2024 Form 2 reports it on Schedule I, Part I, line 11 (instructions PDF
page 25) and the 2025 Form 2 on line 9 (instructions PDF page 23). Line 7
(Montana taxable income) cannot fall below zero.

Each generated household runs three times in one simulation. The bondholder's
taxable_interest_income and us_govt_interest_person are (I, u), (I, 0) and
(0, 0). The first two differ only in the classification input; the third
measures how much of the interest federal AGI includes. The generator keeps
to the input contract the model relies on: u <= I on the same person, with
none of the interest excluded under 26 U.S.C. 135 (us_bonds_for_higher_ed).

Let TI_0 be Montana taxable income without the subtraction, and
u_in = min(u, AGI(I) - AGI(0)) the US interest that federal AGI includes.
u_in = u when the head or spouse holds the bonds. u_in = 0 when a dependent
does, because irs_gross_income leaves a tax-unit dependent's income off the
return. For every household and each year from 2024 to 2026:

1. Same federal base: federal taxable income matches across (I, u) and (I, 0).
2. Accounting: Montana taxable income falls by min(u_in, TI_0).
3. Monotone: Montana income tax does not rise with the subtraction.
4. Bound: Montana taxable income is nonnegative.

The (3) lead-in allows a subtraction only to the extent federal taxable income
included the amount. Under the input contract the subtraction never exceeds
u_in; issue #10780 tracks inputs outside it (US interest above taxable
interest, or interest that section 135 excludes).

From 2025 the enhanced senior deduction phases out at 6% of MAGI, so taxable
income can carry cents. Amount comparisons allow the larger of one cent and
four float32 steps at the compared magnitude.
"""

import hypothesis
import hypothesis.strategies as st
import numpy as np

from policyengine_us import Simulation

YEARS = (2024, 2025, 2026)
VARIANTS = ("with", "without", "no_interest")
SLOW = [hypothesis.HealthCheck.too_slow, hypothesis.HealthCheck.data_too_large]


def tolerance(*values):
    scale = max(abs(float(value)) for value in values)
    return max(0.01, 4 * float(np.spacing(np.float32(scale))))


def bondholder(case):
    # A single filer has no spouse; put the spouse's bonds on the head.
    if case["holder"] == "spouse" and not case["joint"]:
        return "head"
    return case["holder"]


def us_interest(case):
    return round(case["interest"] * case["us_share"])


def build_situation(cases, years):
    people, tax_units, marital_units, households = {}, {}, {}, {}

    def by_year(value):
        return {year: value for year in years}

    for i, case in enumerate(cases):
        holder = bondholder(case)
        inputs = {
            "with": (case["interest"], us_interest(case)),
            "without": (case["interest"], 0),
            "no_interest": (0, 0),
        }
        for variant in VARIANTS:
            interest, amount = inputs[variant]
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
            people[owner]["taxable_interest_income"] = by_year(interest)
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


VARIABLES = (
    "mt_taxable_income",
    "mt_income_tax",
    "taxable_income",
    "adjusted_gross_income",
)


def calculate(cases, years=YEARS):
    """Return {year: {variable: array}}, each array shaped [case, variant]."""
    simulation = Simulation(situation=build_situation(cases, years))
    return {
        year: {
            variable: np.asarray(simulation.calculate(variable, year)).reshape(
                len(cases), len(VARIANTS)
            )
            for variable in VARIABLES
        }
        for year in years
    }


def assert_properties(cases):
    for year, results in calculate(cases).items():
        mt_ti = results["mt_taxable_income"]
        tax = results["mt_income_tax"]
        federal_ti = results["taxable_income"]
        agi = results["adjusted_gross_income"]
        for i, case in enumerate(cases):
            ti_with, ti_without, _ = (float(x) for x in mt_ti[i])
            agi_with_interest, _, agi_no_interest = (float(x) for x in agi[i])
            u_in = min(us_interest(case), agi_with_interest - agi_no_interest)
            context = (year, case, mt_ti[i], tax[i], federal_ti[i], agi[i])
            assert federal_ti[i][0] == federal_ti[i][1], context
            assert ti_with >= 0 and ti_without >= 0, context
            expected = min(u_in, ti_without)
            assert abs((ti_without - ti_with) - expected) <= tolerance(
                ti_without, ti_with
            ), context
            assert tax[i][0] <= tax[i][1] + tolerance(tax[i][1]), context


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
# a dependent holds the bonds, interior cuts, single and joint, and a senior
# whose 2025-2026 deduction phase-out leaves cents in taxable income.
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
    case(False, "head", 89_511, 5_000, 1.0, age=70),
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
    results = calculate(cases, years=(2024, 2025))
    taxable_income_2024 = results[2024]["mt_taxable_income"][:, :2]
    taxable_income_2025 = results[2025]["mt_taxable_income"][:, :2]
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
