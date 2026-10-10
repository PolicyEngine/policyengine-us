"""Household checks of ``marginal_tax_rate_on_capital_gains``.

The capital gains realization response scales a person's long-term gains with
the change in this rate between baseline and reform policy
(``capital_gains_responses.py``), so it has to be the rate on long-term gains.
It used to raise ``capital_gains``, the sum of short- and long-term gains.
That reaches adjusted gross income but not net capital gain, so the rise was
taxed as ordinary income, and raising the top capital gains rate from 20% to
28% left a top-bracket filer's measured rate unchanged.

Invariants, each checked through household simulations for 2026:

1. Statutory rate. A Texas single filer whose only income is long-term gains
   in the 15% or 20% bracket faces that bracket's rate (26 U.S.C. 1(h)(1)),
   plus the 3.8% net investment income tax once modified adjusted gross
   income passes its threshold (26 U.S.C. 1411), plus half that rate where
   each dollar of gains also removes 50 cents of alternative minimum tax
   exemption (26 U.S.C. 55(d)). Texas has no income tax.
2. Reform. With the top capital gains rate set to r, a top-bracket filer's
   rate moves by r less the baseline rate, both measured directly and through
   the behavioral response measurement branches. That holds until the tax at
   the capital gains rates would exceed the tax on all taxable income at the
   ordinary rates, which 26 U.S.C. 1(h)(1) then imposes instead: for r = 40%,
   a filer with $20 million of gains faces the 37% ordinary rate and one with
   $1 million still faces 40%.
3. Differential. The rate measured in a branch equals the finite difference
   between new simulations of the same households, across states, filing
   statuses, wages and gains.
4. Rise. The rise in gains is at least $1,000, is $1,000 for households under
   $1 million, and survives float32 rounding to within 1.2e-4 of itself.

The filers in 1 and 2 have 0.1% of their gains, or $1,000 if more, added to
them, so a rate is exact only where that rise stays inside one bracket; the
examples keep clear of the bracket edges.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings, strategies as st

from policyengine_us import Simulation
from policyengine_us.system import system
from policyengine_us.variables.gov.simulation.capital_gains_responses import (
    CAPITAL_GAINS_MTR_MINIMUM_RISE,
    CAPITAL_GAINS_MTR_RELATIVE_RISE,
    capital_gains_mtr_rise,
)

YEAR = "2026"
AGE = 50
IRS = system.parameters(f"{YEAR}-01-01").gov.irs
CAPITAL_GAINS_RATES = [IRS.capital_gains.rates[bracket] for bracket in "123"]
STANDARD_DEDUCTION = IRS.deductions.standard.amount["SINGLE"]
# Long-term gains at which a single filer with no other income leaves the 0%
# and the 15% brackets.
FIFTEEN_PERCENT_START = int(
    STANDARD_DEDUCTION + IRS.capital_gains.thresholds["1"]["SINGLE"]
)
TWENTY_PERCENT_START = int(
    STANDARD_DEDUCTION + IRS.capital_gains.thresholds["2"]["SINGLE"]
)
ORDINARY_RATES = [IRS.income.bracket.rates[str(bracket)] for bracket in range(1, 8)]
ORDINARY_THRESHOLDS = [
    IRS.income.bracket.thresholds[str(bracket)]["SINGLE"] for bracket in range(1, 7)
]
TOP_ORDINARY_RATE = ORDINARY_RATES[-1]
NIIT = IRS.investment.net_investment_income_tax
AMT_EXEMPTION = IRS.income.amt.exemption
# The alternative minimum tax does not allow the standard deduction, so a
# filer owes it once the exemption has phased out to less than the standard
# deduction. From there until the exemption is gone, each dollar of gains
# removes ``phase_out.rate`` dollars of exemption, taxed at the gains rate.
AMT_PHASE_OUT_RATE = AMT_EXEMPTION.phase_out.rate
AMT_BINDS_FROM = (
    AMT_EXEMPTION.phase_out.start["SINGLE"]
    + (AMT_EXEMPTION.amount["SINGLE"] - STANDARD_DEDUCTION) / AMT_PHASE_OUT_RATE
)
AMT_EXEMPTION_GONE = (
    AMT_EXEMPTION.phase_out.start["SINGLE"]
    + AMT_EXEMPTION.amount["SINGLE"] / AMT_PHASE_OUT_RATE
)
RATE_EDGES = (
    FIFTEEN_PERCENT_START,
    NIIT.threshold["SINGLE"],
    TWENTY_PERCENT_START,
    AMT_BINDS_FROM,
    AMT_EXEMPTION_GONE,
)
# household_net_income is a float32, which resolves 2 ** -23 of its size, and
# the rise is at least 0.1% of it, so the difference alone resolves the rate
# to 1.2e-4. The tax itself is rounded along the way.
RATE_RESOLUTION = 2.5e-4
TOP_RATE = "gov.irs.capital_gains.rates.3"
REFORM_PERIOD = f"{YEAR}-01-01.{YEAR}-12-31"
TOP_BRACKET_GAINS = (1_000_000, 20_000_000, 100_000_000)
SIMULATION_SETTINGS = dict(
    deadline=None,
    derandomize=True,
    database=None,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


def statutory_rate(gains):
    """Federal rate on one more dollar of a single filer's only income."""
    if gains < FIFTEEN_PERCENT_START:
        rate = CAPITAL_GAINS_RATES[0]
    elif gains < TWENTY_PERCENT_START:
        rate = CAPITAL_GAINS_RATES[1]
    else:
        rate = CAPITAL_GAINS_RATES[2]
    net_investment_income_tax = NIIT.rate if gains > NIIT.threshold["SINGLE"] else 0
    alternative_minimum_tax = (
        AMT_PHASE_OUT_RATE * rate if AMT_BINDS_FROM < gains < AMT_EXEMPTION_GONE else 0
    )
    return rate + net_investment_income_tax + alternative_minimum_tax


def top_bracket_rate(gains, top_rate):
    """Regular tax rate on the next dollar of a top-bracket filer's gains.

    26 U.S.C. 1(h)(1): the tax "shall not exceed" the tax at the capital gains
    rates, so it is the smaller of that and the tax on all taxable income at
    the ordinary rates (Schedule D Tax Worksheet, line 47).
    """
    taxable_income = gains - STANDARD_DEDUCTION
    assert taxable_income > ORDINARY_THRESHOLDS[-1]
    tax_at_capital_gains_rates = CAPITAL_GAINS_RATES[1] * (
        TWENTY_PERCENT_START - FIFTEEN_PERCENT_START
    ) + top_rate * (gains - TWENTY_PERCENT_START)
    edges = [0, *ORDINARY_THRESHOLDS, taxable_income]
    tax_at_ordinary_rates = sum(
        rate * (upper - lower)
        for rate, lower, upper in zip(ORDINARY_RATES, edges, edges[1:])
    )
    if tax_at_capital_gains_rates < tax_at_ordinary_rates:
        return top_rate
    return TOP_ORDINARY_RATE


def clear_of_rate_edges(gains):
    rise = max(CAPITAL_GAINS_MTR_MINIMUM_RISE, CAPITAL_GAINS_MTR_RELATIVE_RISE * gains)
    return all(not edge - 2 * rise <= gains <= edge + rise for edge in RATE_EDGES)


def simulate(households, reform=None):
    """A simulation of ``households``, each a state and its adults.

    An adult is a pair of wages and long-term gains. Two adults are married
    and file jointly.
    """
    situation = {
        key: {}
        for key in (
            "people",
            "tax_units",
            "marital_units",
            "families",
            "spm_units",
            "households",
        )
    }
    for index, (state, adults) in enumerate(households):
        members = []
        for adult, (wages, gains) in enumerate(adults):
            name = f"adult_{index}_{adult}"
            members.append(name)
            situation["people"][name] = {
                "age": {YEAR: AGE},
                "employment_income": {YEAR: wages},
                "long_term_capital_gains": {YEAR: gains},
            }
        for key in ("tax_units", "marital_units", "families", "spm_units"):
            situation[key][f"{key}_{index}"] = {"members": members}
        situation["households"][f"household_{index}"] = {
            "members": members,
            "state_name": {YEAR: state},
        }
    return Simulation(
        situation=situation, reform=reform, spm={"geography_kind": "national"}
    )


def texas_single_filers(gains):
    return [("TX", [(0, amount)]) for amount in gains]


def measured_rate(simulation):
    return simulation.calculate("marginal_tax_rate_on_capital_gains", YEAR)


def top_rate_reform(top_rate):
    return {TOP_RATE: {REFORM_PERIOD: top_rate}}


def test_statutory_rate_is_derived_from_the_2026_schedule():
    # The expectations below come from parameters; these pin what they are.
    assert CAPITAL_GAINS_RATES == [0, 0.15, 0.2]
    assert (FIFTEEN_PERCENT_START, TWENTY_PERCENT_START) == (65_550, 561_600)
    assert (NIIT.rate, NIIT.threshold["SINGLE"]) == (0.038, 200_000)
    assert (AMT_BINDS_FROM, AMT_EXEMPTION_GONE) == (648_000, 680_200)
    assert statutory_rate(100_000) == pytest.approx(0.15)
    assert statutory_rate(300_000) == pytest.approx(0.188)
    assert statutory_rate(660_000) == pytest.approx(0.338)
    assert statutory_rate(20_000_000) == pytest.approx(0.238)
    assert TOP_ORDINARY_RATE == 0.37
    assert top_bracket_rate(20_000_000, 0.3) == 0.3
    assert top_bracket_rate(1_000_000, 0.4) == 0.4
    assert top_bracket_rate(20_000_000, 0.4) == 0.37


@settings(max_examples=8, **SIMULATION_SETTINGS)
@given(
    gains=st.lists(
        st.one_of(
            st.integers(FIFTEEN_PERCENT_START, 800_000),
            st.integers(800_000, 3_000_000_000),
        ).filter(clear_of_rate_edges),
        min_size=1,
        max_size=12,
    )
)
def test_rate_on_long_term_gains_is_the_statutory_rate(gains):
    measured = measured_rate(simulate(texas_single_filers(gains)))

    expected = [statutory_rate(amount) for amount in gains]
    np.testing.assert_allclose(measured, expected, rtol=0, atol=RATE_RESOLUTION)


def test_rate_on_long_term_gains_in_each_bracket():
    # 15%; 15% with the net investment income tax; 20% with it; 20% with it
    # and the alternative minimum tax exemption phasing out; then 20% with it
    # at sizes where float32 resolved a $1,000 rise only to 0.002 and 0.008.
    gains = [100_000, 300_000, 600_000, 660_000, 20_000_000, 100_000_000]

    measured = measured_rate(simulate(texas_single_filers(gains)))

    np.testing.assert_allclose(
        measured,
        [0.15, 0.188, 0.238, 0.338, 0.238, 0.238],
        rtol=0,
        atol=RATE_RESOLUTION,
    )


def test_rate_on_long_term_gains_stacks_on_wages_and_covers_both_spouses():
    simulation = simulate(
        [
            # $60,000 of wages put $200,000 of gains in the 15% bracket and
            # over the net investment income tax threshold.
            ("TX", [(60_000, 200_000)]),
            # Joint filers whose combined gains reach the 20% bracket.
            ("TX", [(0, 500_000), (0, 300_000)]),
        ]
    )

    np.testing.assert_allclose(
        measured_rate(simulation),
        [0.188, 0.238, 0.238],
        rtol=0,
        atol=RATE_RESOLUTION,
    )


# Two ranges of the top rate are left out, where a filer's rate is not the
# smaller of the top rate and the top ordinary rate for every filer here:
# - 28% to 29%. Once the tax at the capital gains rates passes the alternative
#   minimum tax's flat 26% and 28% computation, that computation is the
#   tentative minimum tax, and for a sliver of rates the filer still owes
#   alternative minimum tax and faces 28%: 28.38% to 28.40% with $20 million
#   of gains, 28.074% to 28.078% with $100 million.
# - 37% to 38%. The tax on all taxable income at the ordinary rates becomes
#   the smaller regular tax at 37.09% with $100 million of gains and 37.43%
#   with $20 million, and within the rise of that point the rate is a blend.
TOP_RATES = st.one_of(
    st.floats(CAPITAL_GAINS_RATES[2], 0.28),
    st.floats(0.29, TOP_ORDINARY_RATE),
    st.floats(0.38, 0.4),
)


@settings(max_examples=4, **SIMULATION_SETTINGS)
@given(top_rate=TOP_RATES)
def test_rate_follows_the_top_capital_gains_rate(top_rate):
    simulation = simulate(
        texas_single_filers(TOP_BRACKET_GAINS), reform=top_rate_reform(top_rate)
    )

    np.testing.assert_allclose(
        measured_rate(simulation),
        [top_bracket_rate(gains, top_rate) + NIIT.rate for gains in TOP_BRACKET_GAINS],
        rtol=0,
        atol=RATE_RESOLUTION,
    )


@pytest.mark.parametrize("top_rate", [0.28, 0.4])
def test_measured_rate_change_is_the_statutory_change(top_rate):
    simulation = simulate(
        texas_single_filers(TOP_BRACKET_GAINS), reform=top_rate_reform(top_rate)
    )

    simulation.calculate("relative_capital_gains_mtr_change", YEAR)
    measurements = simulation._behavioral_response_measurements[YEAR]
    baseline_rate = measurements["baseline_capital_gains_mtr"]
    reform_rate = measurements["reform_capital_gains_mtr"]

    np.testing.assert_allclose(
        baseline_rate,
        CAPITAL_GAINS_RATES[2] + NIIT.rate,
        rtol=0,
        atol=RATE_RESOLUTION,
    )
    np.testing.assert_allclose(
        reform_rate - baseline_rate,
        [
            top_bracket_rate(gains, top_rate) - CAPITAL_GAINS_RATES[2]
            for gains in TOP_BRACKET_GAINS
        ],
        rtol=0,
        atol=2 * RATE_RESOLUTION,
    )


def fresh_simulation_rate(households):
    """The rate as a difference between new simulations of ``households``."""
    base = simulate(households)
    net_income = base.person.household("household_net_income", YEAR)
    gains = base.calculate("long_term_capital_gains", YEAR)
    adult_index = base.calculate("adult_index_cg", YEAR)
    rise = capital_gains_mtr_rise(net_income, gains)
    rates = np.zeros_like(net_income)
    for index in (1, 2):
        raised = adult_index == index
        raised_gains = (gains + raised * rise).astype(np.float32)
        people = iter(raised_gains)
        higher = simulate(
            [
                (state, [(wages, float(next(people))) for wages, _ in adults])
                for state, adults in households
            ]
        )
        increase = higher.person.household("household_net_income", YEAR) - net_income
        stored_rise = np.where(raised, raised_gains - gains, 1)
        rates += np.where(raised, 1 - increase / stored_rise, 0)
    return base, rates


ADULT = st.tuples(
    st.sampled_from([0, 20_000, 60_000, 250_000, 2_000_000]),
    st.one_of(
        st.integers(-50_000, 700_000),
        st.integers(700_000, 200_000_000),
    ),
)


@settings(max_examples=5, **SIMULATION_SETTINGS)
@given(
    households=st.lists(
        st.tuples(
            st.sampled_from(["TX", "CA", "NY", "MA", "PA"]),
            st.lists(ADULT, min_size=1, max_size=2),
        ),
        min_size=1,
        max_size=6,
    )
)
def test_branch_rate_matches_new_simulations(households):
    base, expected = fresh_simulation_rate(households)

    np.testing.assert_allclose(measured_rate(base), expected, rtol=0, atol=1e-6)


FLOAT32_AMOUNT = st.floats(-(2.0**36), 2.0**36, width=32)


@settings(max_examples=300, deadline=None, derandomize=True, database=None)
@given(net_income=FLOAT32_AMOUNT, gains=FLOAT32_AMOUNT)
def test_rise_survives_float32_rounding(net_income, gains):
    net_income, gains = np.float32(net_income), np.float32(gains)

    rise = capital_gains_mtr_rise(net_income, gains)

    assert rise >= CAPITAL_GAINS_MTR_MINIMUM_RISE
    if max(abs(net_income), abs(gains)) <= 1_000_000:
        assert rise == CAPITAL_GAINS_MTR_MINIMUM_RISE
    stored_rise = np.float64(np.float32(gains + rise)) - np.float64(gains)
    assert stored_rise > 0
    # Rounding the raised gains moves them by at most half of 2 ** -23 of
    # their size, and the rise is at least 0.1% of the gains.
    assert abs(stored_rise - rise) <= 1.2e-4 * rise
