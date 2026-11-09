"""Invariants for New York's pre-TCJA mortgage debt limits.

N.Y. Tax Law 615(a) computes New York itemized deductions as they existed
immediately before P.L. 115-97, so from 2018 New York keeps the IRC
163(h)(3)(B)-(D) limits: grandfathered debt, incurred on or before October
13, 1987, has no dollar limit and reduces the $1,000,000 acquisition-debt
limit ($500,000 married filing separately); acquisition debt above that limit
and non-acquisition debt count as home equity debt up to $100,000 ($50,000),
and on each home only up to its fair market value less the debt on it
treated as acquisition or grandfathered debt. A fair market value of 0 means
unknown: the home counts as worth at least the debt on it, so only the dollar
limit applies.

Hypothesis draws two homes, each with an acquisition balance and vintage,
non-acquisition debt and a fair market value, around every cutoff and limit,
and checks _ny_qualified_loan_limit:

1. Differential: it equals an independent restatement in the statute's
   order. The restatement places the acquisition limit on the homes in each
   reasonable way, in proportion to each home's other acquisition debt or
   loan by loan in every date order that the origination years allow, and
   keeps the largest home equity debt. It finds the date orders by checking
   every permutation of the homes, not from the model's two explicit orders.
2. Bounds: grandfathered debt <= New York limit <= total debt, and the New
   York limit is at least PE's federal limit for the same acquisition loans.
3. Defaults: with no fair market value and no non-acquisition debt (the
   input defaults), the limit is line 6 plus the acquisition debt above it,
   up to the home equity debt limit. The Hawaii helper gives the same
   limit.
4. Order: swapping the two homes never changes the limit.
5. Monotone: a higher positive fair market value never lowers the limit.
6. Unknown value: setting every fair market value to 0 (unknown) never
   lowers the limit.

For _ny_allowed_interest, PE's federal share for the same loans splits
interest on two homes with no non-acquisition debt into the federally
deductible and non-deductible parts. The New York result lies between the
federal deduction and the interest paid, and equals the federal deduction
when federal law disallows nothing. The federal bound follows from the
limits, not from a floor.

For _ny_deductible_share: the share is at least the unrounded ratio and at
least the ratio rounded half up to three places, and at most one. It exceeds
the unrounded ratio by no more than .0005 plus 5e-13, since the nine-place
rounding treats a scaled ratio within 5e-10 of a half as a tie.

The test reads the limits from the New York and federal parameters for
every filing status in 2018, 2025 and 2026. The properties cannot pass
trivially: the differential compares against a separately written per-home
calculation, and the default and bound checks fail if the fair market value
test, the home equity limit or the acquisition limit is dropped or reversed.

These are for-all properties of the helpers, which YAML cannot state. The
policy outcomes are checked in ny_mortgage_interest_deduction.yaml.
"""

import itertools
import math
from fractions import Fraction

import numpy as np
from hypothesis import example, given, settings
from hypothesis import strategies as st

from policyengine_us.system import system
from policyengine_us.variables.gov.states.hi.tax.income.deductions.itemized.hi_mortgage_interest_deduction import (
    _hi_qualified_loan_limit,
)
from policyengine_us.variables.gov.states.ny.tax.income.taxable_income.deductions.itemized.ny_mortgage_interest_deduction import (
    _ny_allowed_interest,
    _ny_deductible_share,
    _ny_qualified_loan_limit,
)
from policyengine_us.variables.household.expense.tax_unit.mortgage_interest_structure import (
    _debt_by_vintage,
    _qualified_loan_limit,
)

GRANDFATHERED_YEAR = 1987
PRE_TCJA_YEAR = 2017
FILING_STATUSES = (
    "SINGLE",
    "JOINT",
    "SEPARATE",
    "HEAD_OF_HOUSEHOLD",
    "SURVIVING_SPOUSE",
)
TAX_YEARS = (2018, 2025, 2026)


def parameter_limits(year, filing_status):
    p = system.parameters(f"{year}-01-01")
    ny = p.gov.states.ny.tax.income.deductions.itemized.interest
    federal = p.gov.irs.deductions.itemized.interest.mortgage
    return (
        (
            float(ny.home_acquisition_debt_limit[filing_status]),
            float(ny.home_equity_debt_limit[filing_status]),
        ),
        (
            float(federal.pre_tcja_cap[filing_status]),
            float(federal.cap[filing_status]),
        ),
    )


LIMITS = {
    (year, filing_status): parameter_limits(year, filing_status)
    for year in TAX_YEARS
    for filing_status in FILING_STATUSES
}
TOLERANCE = 0.01

YEARS = (0, 1960, 1987, 1988, 2017, 2018, 2025)
BOUNDARY_AMOUNTS = (
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
amounts = st.one_of(
    st.sampled_from(BOUNDARY_AMOUNTS),
    st.integers(0, 3_000_000),
).map(float)
# (acquisition balance, origination year, non-acquisition debt, fair market value)
homes = st.tuples(amounts, st.sampled_from(YEARS), amounts, amounts)


def grandfathered(year):
    return 0 < year <= GRANDFATHERED_YEAR


def model_limit(pair, limits):
    grandfathered_debts = [
        np.array([balance if grandfathered(year) else 0.0])
        for balance, year, _, _ in pair
    ]
    other_debts = [
        np.array([0.0 if grandfathered(year) else balance])
        for balance, year, _, _ in pair
    ]
    return float(
        _ny_qualified_loan_limit(
            grandfathered_debts,
            other_debts,
            [np.array([year]) for _, year, _, _ in pair],
            [np.array([home[2]]) for home in pair],
            [np.array([home[3]]) for home in pair],
            *limits,
        )[0]
    )


def statute(pair, limits):
    """IRC 163(h)(3)(B)(ii), (C) and (D) before P.L. 115-97, home by home."""
    acquisition_limit, home_equity_limit = limits
    old = sum(balance for balance, year, _, _ in pair if grandfathered(year))
    other = sum(balance for balance, year, _, _ in pair if not grandfathered(year))
    # (D)(ii): grandfathered debt reduces the $1,000,000 limit.
    other_allowed = min(other, max(0.0, acquisition_limit - old))

    def home_equity(placed):
        total = 0.0
        for (balance, year, non_acquisition, fair_market_value), on_home in zip(
            pair, placed
        ):
            if grandfathered(year):
                on_home, excess = balance, 0.0
            else:
                excess = balance - on_home
            # (C)(i): no more than fair market value less acquisition debt. A
            # value of 0 means unknown and sets no such limit.
            room = (
                max(0.0, fair_market_value - on_home)
                if fair_market_value > 0
                else math.inf
            )
            total += min(excess + non_acquisition, room)
        return total

    # The allowance shared in proportion to each home's other debt.
    placements = [
        [
            0.0
            if grandfathered(year) or other == 0
            else other_allowed * balance / other
            for balance, year, _, _ in pair
        ]
    ]
    # The allowance placed loan by loan, oldest first, so the most recent
    # debt is the excess. Loans from the same year go in either order, and an
    # unknown year (0) is the most recent.
    dates = [year if year > 0 else math.inf for _, year, _, _ in pair]
    for order in itertools.permutations(range(len(pair))):
        if any(dates[a] > dates[b] for a, b in zip(order, order[1:])):
            continue
        remaining = other_allowed
        placed = [0.0] * len(pair)
        for index in order:
            balance, year = pair[index][0], pair[index][1]
            if not grandfathered(year):
                placed[index] = min(balance, remaining)
                remaining -= placed[index]
        placements.append(placed)
    # (C)(ii): the aggregate home equity limit, on the taxpayer's best placement.
    best = max(home_equity(placed) for placed in placements)
    return old + other_allowed + min(best, home_equity_limit)


def federal_limit(pair, limits):
    debt = _debt_by_vintage(
        [np.array([home[0]]) for home in pair],
        [np.array([home[1]]) for home in pair],
        GRANDFATHERED_YEAR,
        PRE_TCJA_YEAR,
    )
    return float(_qualified_loan_limit(*debt, *limits)[0])


SETTINGS = dict(max_examples=400, deadline=None, derandomize=True)


def test_new_york_limits_are_the_statutory_amounts():
    for (year, filing_status), (ny_limits, _) in LIMITS.items():
        expected = (
            (500_000, 50_000) if filing_status == "SEPARATE" else (1_000_000, 100_000)
        )
        assert ny_limits == expected, (year, filing_status)


@settings(**SETTINGS)
@given(first=homes, second=homes, status=st.sampled_from(sorted(LIMITS)))
# Loans from the same year, where only the second home's loan going first
# gives the full home equity debt: a fixed order fails the differential or
# the swap.
@example(
    first=(900_000.0, 2018, 0.0, 540_000.0),
    second=(900_000.0, 2018, 0.0, 150_000.0),
    status=(2025, "JOINT"),
)
# The same homes with the second loan's year unknown: it counts as the most
# recent, so the main home's loan goes first and the second home's room of
# $50,000 binds.
@example(
    first=(900_000.0, 2017, 0.0, 540_000.0),
    second=(900_000.0, 0, 0.0, 150_000.0),
    status=(2025, "JOINT"),
)
# Loans from different years, where sharing the limit gives more home equity
# debt than date order does.
@example(
    first=(900_000.0, 2017, 0.0, 3_000_000.0),
    second=(900_000.0, 2018, 0.0, 120_000.0),
    status=(2025, "JOINT"),
)
def test_new_york_qualified_loan_limit_properties(first, second, status):
    ny_limits, federal_limits = LIMITS[status]
    pair = [first, second]
    limit = model_limit(pair, ny_limits)
    old = sum(home[0] for home in pair if grandfathered(home[1]))
    total = sum(home[0] + home[2] for home in pair)

    # 1. Differential.
    assert abs(limit - statute(pair, ny_limits)) <= TOLERANCE
    # 2. Bounds.
    assert old - TOLERANCE <= limit <= total + TOLERANCE
    assert limit >= federal_limit(pair, federal_limits) - TOLERANCE
    # 3. Defaults: no fair market value and no non-acquisition debt.
    acquisition_limit, home_equity_limit = ny_limits
    defaults = [(home[0], home[1], 0.0, 0.0) for home in pair]
    acquisition = sum(home[0] for home in pair)
    line_6 = min(max(old, acquisition_limit), acquisition)
    expected = line_6 + min(acquisition - line_6, home_equity_limit)
    assert abs(model_limit(defaults, ny_limits) - expected) <= TOLERANCE
    hawaii = float(
        _hi_qualified_loan_limit(
            np.array([old]), np.array([acquisition - old]), *ny_limits
        )[0]
    )
    assert abs(expected - hawaii) <= TOLERANCE
    # 4. Order.
    assert abs(limit - model_limit([second, first], ny_limits)) <= TOLERANCE
    # 5. Monotone in a positive fair market value.
    richer = [
        (home[0], home[1], home[2], home[3] + 250_000 if home[3] > 0 else 0.0)
        for home in pair
    ]
    assert model_limit(richer, ny_limits) >= limit - TOLERANCE
    # 6. An unknown value (0) never lowers the limit.
    unknown = [(home[0], home[1], home[2], 0.0) for home in pair]
    assert model_limit(unknown, ny_limits) >= limit - TOLERANCE


@settings(**SETTINGS)
@given(
    interest=amounts,
    first=homes,
    second=homes,
    status=st.sampled_from(sorted(LIMITS)),
)
def test_new_york_allowed_interest_without_non_acquisition_debt(
    interest, first, second, status
):
    ny_limits, federal_limits = LIMITS[status]
    pair = [(home[0], home[1], 0.0, home[3]) for home in (first, second)]
    acquisition = sum(home[0] for home in pair)
    if acquisition > 0:
        federal_share = min(1.0, federal_limit(pair, federal_limits) / acquisition)
    else:
        federal_share = 1.0
    deductible = interest * federal_share
    non_deductible = interest - deductible
    share = _ny_deductible_share(
        np.array([model_limit(pair, ny_limits)]), np.array([acquisition])
    )
    allowed = float(
        _ny_allowed_interest(
            np.array([deductible]),
            np.array([non_deductible]),
            np.array([0.0]),
            share,
        )[0]
    )
    assert deductible - TOLERANCE <= allowed <= interest + TOLERANCE
    if non_deductible == 0:
        assert allowed == deductible


@settings(**SETTINGS)
@given(limit=amounts, debt=amounts)
@example(limit=1_001.0, debt=2_000.0)
def test_new_york_deductible_share_is_the_larger_method(limit, debt):
    debt = max(debt, 1.0)
    limit = min(limit, debt)
    share = float(_ny_deductible_share(np.array([limit]), np.array([debt]))[0])
    ratio = limit / debt
    # Rounded half up to three places, computed exactly.
    exact = Fraction(int(limit), int(debt))
    rounded = math.floor(exact * 1_000 + Fraction(1, 2)) / 1_000
    assert share >= ratio - 1e-12
    assert share >= rounded - 1e-12
    assert share <= 1 + 1e-12
    assert share - ratio <= 0.0005 + 1e-12
