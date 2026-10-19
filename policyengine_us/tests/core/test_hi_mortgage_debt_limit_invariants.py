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
6. Share: line 11, the limit over total debt "rounded to three places", lies
   in [0, 1], within half a thousandth of the exact ratio and, for the drawn
   balances, at or above the federal (exact) share. It is the same whether
   the balances arrive in single precision, as in a simulation, or double.
7. Line 12: the Hawaii deduction lies between the federal deduction and the
   interest paid, equals the federal deduction when federal law disallows
   nothing (so a deduction supplied directly is not limited again), and
   otherwise equals interest paid times line 11 unless that would fall below
   the federal amount.

These are for-all properties of the helpers, which YAML cannot state. The
policy outcomes and interest proration are checked in
hi_mortgage_interest_deduction.yaml.
"""

import numpy as np
from hypothesis import given, settings
from hypothesis import strategies as st

from policyengine_us.variables.gov.states.hi.tax.income.deductions.itemized.hi_mortgage_interest_deduction import (
    _hi_allowed_interest,
    _hi_deductible_share,
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

    # 6. Share.
    share = float(_hi_deductible_share(np.array([limit]), np.array([total]))[0])
    assert 0 <= share <= 1
    if total > 0:
        assert abs(share - limit / total) <= 0.0005 + 1e-9
        assert share >= federal_limit(pair, federal_limits) / total - 1e-9
    else:
        assert share == 1
    single = _hi_deductible_share(
        np.array([limit], dtype=np.float32), np.array([total], dtype=np.float32)
    )
    assert float(single[0]) == share


amounts = st.one_of(st.just(0.0), st.floats(0, 500_000, allow_nan=False))


@settings(**SETTINGS)
@given(
    deductible=amounts,
    non_deductible=amounts,
    share=st.one_of(st.sampled_from((0.0, 0.5, 0.733, 1.0)), st.floats(0, 1)),
)
def test_hawaii_allowed_interest_properties(deductible, non_deductible, share):
    allowed = float(
        _hi_allowed_interest(
            np.array([deductible]), np.array([non_deductible]), np.array([share])
        )[0]
    )
    paid = deductible + non_deductible
    # 7. Line 12.
    assert deductible - TOLERANCE <= allowed <= paid + TOLERANCE
    if non_deductible == 0:
        assert allowed == deductible
    else:
        assert abs(allowed - max(paid * share, deductible)) <= TOLERANCE


def test_hawaii_share_rounds_half_up_to_three_places():
    limits = np.array([550_000.0, 1_100_000.0, 1_100_000.0, 0.0])
    debt = np.array([1_760_000.0, 1_500_000.0, 1_300_000.0, 0.0])
    # .3125 rounds up to .313; .7333 down to .733; .8462 down to .846; no
    # balance gives one.
    np.testing.assert_allclose(
        _hi_deductible_share(limits, debt), [0.313, 0.733, 0.846, 1.0]
    )
    # .97449999 rounds down, in single precision too.
    near_tie = _hi_deductible_share(
        np.array([1_100_000], dtype=np.float32),
        np.array([1_128_784], dtype=np.float32),
    )
    np.testing.assert_array_equal(near_tie, [0.974])
