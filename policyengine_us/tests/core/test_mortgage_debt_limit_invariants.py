"""Invariants for the federal acquisition-debt limits on mortgage interest.

26 U.S.C. 163(h)(3) limits deductible mortgage interest by the vintage of
each loan:

- grandfathered debt, incurred on or before October 13, 1987, is acquisition
  debt with no dollar limit, and it reduces the $1,000,000 limit
  ($500,000 married filing separately) for other debt ((h)(3)(D));
- debt incurred on or before December 15, 2017 keeps that $1,000,000 limit,
  and for taxable years after 2017 debt incurred later has a $750,000 limit
  ($375,000), reduced by the earlier debt treated as acquisition debt
  ((h)(3)(F)(i)(II) and (IV)).

IRS Publication 936 (2025), Table 1 (PDF page 14), computes the qualified loan
limit in that order, reducing each limit by grandfathered debt once ("The
limits above are reduced (but not below zero) by the amount of your
grandfathered debt", PDF page 12). Interest is deductible in the ratio of the
limit to the total balance (lines 12-15); the model uses the exact ratio, where
line 14 rounds it to three decimals.

The model stores two loans per tax unit with a balance and an origination
year. Hypothesis draws pairs of loans around every cutoff and limit and checks
the model's helpers against two independent restatements, one line by line
from Table 1 with its "stop here" branch and one in the statute's order:

1. Differential: the helpers equal both restatements.
2. Bounds: grandfathered debt <= qualified limit <= total debt; the limit is
   at least min(total debt, the post-2017 limit) and at most
   max(grandfathered debt, the $1,000,000 limit).
3. Order: swapping the two loans never changes the limit.
4. Monotone: a larger balance, or an older vintage, never lowers the limit.

These are for-all properties of the helpers, which YAML cannot state. The
policy outcomes, parameter lookups for every filing status, and the interest
proration and accounting are checked in deductible_mortgage_interest_tax_unit.yaml,
including vectorized runs that mix filing statuses and vintages.

Cutoff years are written here, not read from the parameters: only the year is
known, so 1987 counts as on or before October 13, 1987 and 2017 as on or
before December 15, 2017. An unknown year (0) counts as post-2017 debt.
"""

import numpy as np
from hypothesis import given, settings
from hypothesis import strategies as st

from policyengine_us.variables.household.expense.tax_unit.mortgage_interest_structure import (
    _debt_by_vintage,
    _qualified_loan_limit,
)

GRANDFATHERED_YEAR = 1987
PRE_TCJA_YEAR = 2017
# (limit for debt on or before December 15, 2017, limit for later debt)
LIMITS = {
    "2018+": (1_000_000, 750_000),
    "2018+ separate": (500_000, 375_000),
    "pre-2018": (1_000_000, 1_000_000),
    "pre-2018 separate": (500_000, 500_000),
}
TOLERANCE = 0.01

YEARS = (0, 1960, 1986, 1987, 1988, 2000, 2016, 2017, 2018, 2025)
BOUNDARY_BALANCES = (0, 1, 375_000, 500_000, 750_000, 775_000, 1_000_000)
balances = st.one_of(
    st.sampled_from(BOUNDARY_BALANCES),
    st.integers(0, 3_000_000),
).map(float)
loans = st.tuples(balances, st.sampled_from(YEARS))


def vintage(year):
    if year <= 0:
        return "post"
    if year <= GRANDFATHERED_YEAR:
        return "grandfathered"
    if year <= PRE_TCJA_YEAR:
        return "pre"
    return "post"


def split(loan_list):
    debt = {"grandfathered": 0.0, "pre": 0.0, "post": 0.0}
    for balance, year in loan_list:
        debt[vintage(year)] += balance
    return debt["grandfathered"], debt["pre"], debt["post"]


def table_1(loan_list, limits):
    """Publication 936 (2025) Table 1, lines 1-11, with its branch."""
    pre_limit, post_limit = limits
    line_1, line_2, line_7 = split(loan_list)
    line_3 = pre_limit
    line_4 = max(line_1, line_3)
    line_5 = line_1 + line_2
    line_6 = min(line_4, line_5)
    # "If you have no home acquisition debt incurred after December 15, 2017,
    # or the amount on line 6 is $750,000 ... or more, line 6 is your
    # qualified loan limit."
    if line_7 == 0 or line_6 >= post_limit:
        return line_6
    line_8 = post_limit
    line_9 = max(line_6, line_8)
    line_10 = line_6 + line_7
    return min(line_9, line_10)


def statute(loan_list, limits):
    """26 U.S.C. 163(h)(3)(B)(ii), (D) and (F), applied in order."""
    pre_limit, post_limit = limits
    grandfathered, pre, post = split(loan_list)
    allowed_pre = min(pre, max(0.0, pre_limit - grandfathered))
    allowed_post = min(post, max(0.0, post_limit - grandfathered - allowed_pre))
    return grandfathered + allowed_pre + allowed_post


def model_limit(loan_list, limits):
    debt = _debt_by_vintage(
        [np.array([balance]) for balance, _ in loan_list],
        [np.array([year]) for _, year in loan_list],
        GRANDFATHERED_YEAR,
        PRE_TCJA_YEAR,
    )
    return float(_qualified_loan_limit(*debt, *limits)[0])


SETTINGS = dict(max_examples=400, deadline=None, derandomize=True)


@settings(**SETTINGS)
@given(first=loans, second=loans, limits=st.sampled_from(sorted(LIMITS)))
def test_qualified_loan_limit_properties(first, second, limits):
    limits = LIMITS[limits]
    pair = [first, second]
    limit = model_limit(pair, limits)
    grandfathered, pre, post = split(pair)
    total = grandfathered + pre + post

    # 1. Differential.
    assert abs(limit - table_1(pair, limits)) <= TOLERANCE
    assert abs(limit - statute(pair, limits)) <= TOLERANCE

    # 2. Bounds.
    assert grandfathered - TOLERANCE <= limit <= total + TOLERANCE
    assert limit >= min(total, limits[1]) - TOLERANCE
    assert limit <= max(grandfathered, limits[0]) + TOLERANCE

    # 3. Order.
    assert abs(model_limit([second, first], limits) - limit) <= TOLERANCE

    # 4. Monotone in balances and in vintage.
    for i, (balance, year) in enumerate(pair):
        bigger = list(pair)
        bigger[i] = (balance + 100_000, year)
        assert model_limit(bigger, limits) >= limit - TOLERANCE
        for older_year in YEARS:
            older = ("grandfathered", "pre", "post").index(vintage(older_year))
            if older <= ("grandfathered", "pre", "post").index(vintage(year)):
                moved = list(pair)
                moved[i] = (balance, older_year)
                assert model_limit(moved, limits) >= limit - TOLERANCE


def test_vintage_split_conserves_debt():
    balances = np.array([100.0, 200.0, 300.0, 400.0, 500.0])
    years = np.array([0, 1987, 1988, 2017, 2018])
    debt = _debt_by_vintage([balances], [years], GRANDFATHERED_YEAR, PRE_TCJA_YEAR)
    np.testing.assert_array_equal(debt[0], [0, 200, 0, 0, 0])
    np.testing.assert_array_equal(debt[1], [0, 0, 300, 400, 0])
    np.testing.assert_array_equal(debt[2], [100, 0, 0, 0, 500])
    np.testing.assert_array_equal(sum(debt), balances)
