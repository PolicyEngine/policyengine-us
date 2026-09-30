"""Invariants of the NYC school tax credit income tests.

NY Tax Law § 606(ggg)(2) bases the credit on income as defined in RPTL
§ 425(4)(b)(ii): federal adjusted gross income reduced by IRA distributions to
the extent included in it. § 606(ggg)(4-b) denies the rate reduction amount to
any taxpayer with that income over $500,000, and its tables compute the amount
on city taxable income, which is "Not applicable" over $500,000. Each test
evaluates a grid of tax units in one vectorized simulation and checks that:

1. the rate reduction amount is eligible exactly when income and city taxable
   income are both at most $500,000, so neither test substitutes for the
   other;
2. the rate reduction amount matches the statutory tables applied to city
   taxable income (a differential check against the text of § 606(ggg)(4-b),
   whose second-band base amounts are rounded; see #8947) and is zero when
   ineligible;
3. school tax credit income equals federal AGI minus the head's and spouse's
   IRA and SEP distributions, is never above AGI, and ignores dependents'
   distributions and non-IRA retirement distributions, whether AGI is an input
   or computed from income sources; and
4. outside NYC, income is zero and the rate reduction amount is ineligible.
"""

import itertools

import numpy as np

from policyengine_us import Simulation

YEAR = 2025
LIMIT = 500_000

INCOMES = [-10_000, 0, 250_000, 499_999, 500_000, 500_001, 750_000]
TAXABLE_INCOMES = [
    -10_000,
    0,
    12_000,
    14_400,
    21_600,
    300_000,
    499_999,
    500_000,
    500_001,
    750_000,
]
FILING_STATUSES = [
    "SINGLE",
    "JOINT",
    "HEAD_OF_HOUSEHOLD",
    "SURVIVING_SPOUSE",
    "SEPARATE",
]

# § 606(ggg)(4-b)(A)-(C): first-band ceiling and second-band base amount.
TABLES = {
    "JOINT": (21_600, 37),
    "SURVIVING_SPOUSE": (21_600, 37),
    "HEAD_OF_HOUSEHOLD": (14_400, 25),
    "SINGLE": (12_000, 21),
    "SEPARATE": (12_000, 21),
}
LOW_RATE = 0.00171
EXCESS_RATE = 0.00228
# The model carries the first band into the second at the marginal rate
# (e.g. 12,000 x 0.171% = 20.52) where the statute prints rounded base
# amounts (21), a gap of at most 0.48 (#8947).
TOLERANCE = 0.5


def statutory_rate_reduction(taxable_income, filing_status):
    ceiling, base = TABLES[filing_status]
    taxable_income = max(taxable_income, 0)
    if taxable_income > LIMIT:
        return 0
    if taxable_income <= ceiling:
        return LOW_RATE * taxable_income
    return base + EXCESS_RATE * (taxable_income - ceiling)


def eligibility_grid(in_nyc=True):
    grid = list(itertools.product(INCOMES, TAXABLE_INCOMES, FILING_STATUSES))
    situation = {"people": {}, "tax_units": {}, "households": {}}
    for i, (income, taxable_income, filing_status) in enumerate(grid):
        person = f"p{i}"
        situation["people"][person] = {"age": {YEAR: 45}}
        situation["tax_units"][f"tu{i}"] = {
            "members": [person],
            "filing_status": {YEAR: filing_status},
            "nyc_school_credit_income": {YEAR: income},
            "nyc_taxable_income": {YEAR: taxable_income},
        }
        situation["households"][f"hh{i}"] = {
            "members": [person],
            "state_code": {YEAR: "NY"},
            "in_nyc": {YEAR: in_nyc},
        }
    return grid, Simulation(situation=situation)


def test_rate_reduction_requires_both_income_tests():
    grid, sim = eligibility_grid()
    eligible = sim.calculate(
        "nyc_school_tax_credit_rate_reduction_amount_eligible", YEAR
    )
    expected = np.array(
        [
            income <= LIMIT and taxable_income <= LIMIT
            for income, taxable_income, _ in grid
        ]
    )
    assert (eligible == expected).all()


def test_rate_reduction_amount_follows_statutory_tables():
    grid, sim = eligibility_grid()
    amount = sim.calculate("nyc_school_tax_credit_rate_reduction_amount", YEAR)
    expected = np.array(
        [
            (
                statutory_rate_reduction(taxable_income, filing_status)
                if income <= LIMIT
                else 0
            )
            for income, taxable_income, filing_status in grid
        ]
    )
    assert (amount >= 0).all()
    assert np.abs(amount - expected).max() <= TOLERANCE
    # Ineligible units get exactly zero, not a rounding residual.
    ineligible = np.array(
        [income > LIMIT or taxable_income > LIMIT for income, taxable_income, _ in grid]
    )
    assert (amount[ineligible] == 0).all()


INCOME_GRID = list(
    itertools.product(
        [0, 100_000, 600_000],  # AGI
        [0, 25_000],  # head IRA distributions
        [0, 10_000],  # head SEP distributions
        [0, 50_000],  # head 401(k) distributions
        [0, 20_000],  # spouse IRA distributions
        [0, 5_000],  # dependent IRA distributions
    )
)


def family(i, head, spouse, dependent, tax_unit_inputs, in_nyc=True):
    names = [f"f{i}_head", f"f{i}_spouse", f"f{i}_child"]
    people = {
        names[0]: {"age": {YEAR: 45}, **head},
        names[1]: {"age": {YEAR: 45}, **spouse},
        names[2]: {
            "age": {YEAR: 17},
            "is_tax_unit_dependent": {YEAR: True},
            **dependent,
        },
    }
    tax_unit = {"members": names, **tax_unit_inputs}
    household = {
        "members": names,
        "state_code": {YEAR: "NY"},
        "in_nyc": {YEAR: in_nyc},
    }
    return people, tax_unit, household


def build(families):
    situation = {"people": {}, "tax_units": {}, "households": {}}
    for i, (people, tax_unit, household) in enumerate(families):
        situation["people"].update(people)
        situation["tax_units"][f"tu{i}"] = tax_unit
        situation["households"][f"hh{i}"] = household
    return Simulation(situation=situation)


def test_income_subtracts_only_included_ira_distributions():
    families = [
        family(
            i,
            head={
                "taxable_ira_distributions": {YEAR: head_ira},
                "taxable_sep_distributions": {YEAR: head_sep},
                "taxable_401k_distributions": {YEAR: head_401k},
            },
            spouse={"taxable_ira_distributions": {YEAR: spouse_ira}},
            dependent={"taxable_ira_distributions": {YEAR: dependent_ira}},
            tax_unit_inputs={"adjusted_gross_income": {YEAR: agi}},
        )
        for i, (
            agi,
            head_ira,
            head_sep,
            head_401k,
            spouse_ira,
            dependent_ira,
        ) in enumerate(INCOME_GRID)
    ]
    income = build(families).calculate("nyc_school_credit_income", YEAR)
    expected = np.array(
        [
            agi - (head_ira + head_sep + spouse_ira)
            for agi, head_ira, head_sep, _, spouse_ira, _ in INCOME_GRID
        ]
    )
    agi = np.array([row[0] for row in INCOME_GRID])
    assert (income == expected).all()
    assert (income <= agi).all()


def test_income_matches_computed_agi_less_ira_distributions():
    grid = list(
        itertools.product(
            [0, 200_000, 480_000],  # head wages
            [0, 100_000],  # head IRA distributions
            [0, 30_000],  # spouse SEP distributions
            [0, 5_000],  # dependent IRA distributions
        )
    )
    families = [
        family(
            i,
            head={
                "employment_income": {YEAR: wages},
                "taxable_ira_distributions": {YEAR: head_ira},
            },
            spouse={"taxable_sep_distributions": {YEAR: spouse_sep}},
            dependent={"taxable_ira_distributions": {YEAR: dependent_ira}},
            tax_unit_inputs={},
        )
        for i, (wages, head_ira, spouse_sep, dependent_ira) in enumerate(grid)
    ]
    sim = build(families)
    agi = sim.calculate("adjusted_gross_income", YEAR)
    income = sim.calculate("nyc_school_credit_income", YEAR)
    subtracted = np.array(
        [head_ira + spouse_sep for _, head_ira, spouse_sep, _ in grid]
    )
    assert np.allclose(agi - income, subtracted)
    assert (income <= agi).all()


def test_outside_nyc_income_is_zero_and_rate_reduction_ineligible():
    _, sim = eligibility_grid(in_nyc=False)
    assert not sim.calculate(
        "nyc_school_tax_credit_rate_reduction_amount_eligible", YEAR
    ).any()
    people, tax_unit, household = family(
        0,
        head={"taxable_ira_distributions": {YEAR: 25_000}},
        spouse={},
        dependent={},
        tax_unit_inputs={"adjusted_gross_income": {YEAR: 300_000}},
        in_nyc=False,
    )
    assert (
        build([(people, tax_unit, household)]).calculate(
            "nyc_school_credit_income", YEAR
        )[0]
        == 0
    )
