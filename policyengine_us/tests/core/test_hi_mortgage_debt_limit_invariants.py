"""Invariants for Hawaii's mortgage debt limits.

HRS 235-2.4(j)(3) (235-2.4(i)(3) from 2026) makes IRC 163(h)(3)(F)
inoperative, so Hawaii keeps the pre-TCJA limits for debt incurred at any
time. IRS Publication 936 (2017), Table 1 (PDF page 11), computes them:
grandfathered debt, incurred on or before October 13, 1987, has no dollar
limit and reduces the $1,000,000 acquisition-debt limit ($500,000 married
filing separately); up to $100,000 ($50,000) of debt above that limit counts
as home equity debt (Figure A, note 3, PDF page 3).

Hypothesis draws pairs of loans around every cutoff and limit and checks
_hi_qualified_loan_limit against two independent restatements, one line by
line from Table 1 and one in the statute's order, and against the federal
helper:

1. Differential: the helper equals both restatements.
2. Bounds: grandfathered debt <= Hawaii limit <= total debt, and the Hawaii
   limit is at least the federal limit for the same loans, so Hawaii never
   allows less interest than federal law and never more than was paid.
3. Order: swapping the two loans never changes the limit.
4. Vintage: Hawaii has one limit for debt incurred after October 13, 1987, so
   moving a loan between 2017 and 2018 never changes the limit, while moving
   it into the grandfathered years never lowers it.
5. Monotone: a larger balance never lowers the limit.

These are for-all properties of the helper, which YAML cannot state. The
policy outcomes and interest proration are checked in
hi_mortgage_interest_deduction.yaml.
"""

import numpy as np
from hypothesis import given, settings
from hypothesis import strategies as st

from policyengine_us.variables.gov.states.hi.tax.income.deductions.itemized.hi_mortgage_interest_deduction import (
    _hi_qualified_loan_limit,
)
from policyengine_us.variables.household.expense.tax_unit.mortgage_interest_structure import (
    _debt_by_vintage,
    _qualified_loan_limit,
)

GRANDFATHERED_YEAR = 1987
PRE_TCJA_YEAR = 2017
# Filing status -> ((Hawaii acquisition limit, Hawaii home equity limit),
# (federal limit for debt from 2017 or earlier, federal limit for later debt)).
LIMITS = {
    "other": ((1_000_000, 100_000), (1_000_000, 750_000)),
    "separate": ((500_000, 50_000), (500_000, 375_000)),
}
TOLERANCE = 0.01

YEARS = (0, 1960, 1986, 1987, 1988, 2000, 2016, 2017, 2018, 2025)
BOUNDARY_BALANCES = (
    0,
    1,
    50_000,
    100_000,
    375_000,
    500_000,
    550_000,
    750_000,
    1_000_000,
    1_100_000,
)
balances = st.one_of(
    st.sampled_from(BOUNDARY_BALANCES),
    st.integers(0, 3_000_000),
).map(float)
loans = st.tuples(balances, st.sampled_from(YEARS))


def grandfathered(year):
    return 0 < year <= GRANDFATHERED_YEAR


def split(loan_list):
    old = sum(balance for balance, year in loan_list if grandfathered(year))
    other = sum(balance for balance, year in loan_list if not grandfathered(year))
    return old, other


def table_1(loan_list, limits):
    """Publication 936 (2017) Table 1, lines 1-8."""
    acquisition_limit, home_equity_limit = limits
    line_1, line_2 = split(loan_list)
    line_3 = acquisition_limit
    line_4 = max(line_1, line_3)
    line_5 = line_1 + line_2
    line_6 = min(line_4, line_5)
    # Debt above the acquisition limit, up to the home equity limit.
    line_7 = min(line_5 - line_6, home_equity_limit)
    return line_6 + line_7


def statute(loan_list, limits):
    """26 U.S.C. 163(h)(3)(B)(ii), (C)(ii) and (D) without (F), in order."""
    acquisition_limit, home_equity_limit = limits
    old, other = split(loan_list)
    acquisition = min(other, max(0.0, acquisition_limit - old))
    home_equity = min(home_equity_limit, other - acquisition)
    return old + acquisition + home_equity


def model_limit(loan_list, limits):
    debt = _debt_by_vintage(
        [np.array([balance]) for balance, _ in loan_list],
        [np.array([year]) for _, year in loan_list],
        GRANDFATHERED_YEAR,
        PRE_TCJA_YEAR,
    )
    old, pre, post = debt
    return float(_hi_qualified_loan_limit(old, pre + post, *limits)[0])


def federal_limit(loan_list, limits):
    debt = _debt_by_vintage(
        [np.array([balance]) for balance, _ in loan_list],
        [np.array([year]) for _, year in loan_list],
        GRANDFATHERED_YEAR,
        PRE_TCJA_YEAR,
    )
    return float(_qualified_loan_limit(*debt, *limits)[0])


SETTINGS = dict(max_examples=400, deadline=None, derandomize=True)


@settings(**SETTINGS)
@given(first=loans, second=loans, status=st.sampled_from(sorted(LIMITS)))
def test_hawaii_qualified_loan_limit_properties(first, second, status):
    hawaii_limits, federal_limits = LIMITS[status]
    pair = [first, second]
    limit = model_limit(pair, hawaii_limits)
    old, other = split(pair)
    total = old + other

    # 1. Differential.
    assert abs(limit - table_1(pair, hawaii_limits)) <= TOLERANCE
    assert abs(limit - statute(pair, hawaii_limits)) <= TOLERANCE

    # 2. Bounds.
    assert old - TOLERANCE <= limit <= total + TOLERANCE
    assert limit >= federal_limit(pair, federal_limits) - TOLERANCE

    # 3. Order.
    assert abs(model_limit([second, first], hawaii_limits) - limit) <= TOLERANCE

    for i, (balance, year) in enumerate(pair):
        # 4. Vintage.
        for other_year in YEARS:
            moved = list(pair)
            moved[i] = (balance, other_year)
            moved_limit = model_limit(moved, hawaii_limits)
            if grandfathered(other_year) == grandfathered(year):
                assert abs(moved_limit - limit) <= TOLERANCE
            elif grandfathered(other_year):
                assert moved_limit >= limit - TOLERANCE

        # 5. Monotone.
        bigger = list(pair)
        bigger[i] = (balance + 100_000, year)
        assert model_limit(bigger, hawaii_limits) >= limit - TOLERANCE
