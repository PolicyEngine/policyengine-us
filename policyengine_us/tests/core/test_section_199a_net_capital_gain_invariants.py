"""Invariants for the net capital gain in the QBI deduction's income limit.

26 USC 199A(a)(2)(B) subtracts net capital gain from taxable income, and
Treas. Reg. 1.199A-1(b)(3) defines it as "net capital gain as defined in
section 1222(11) plus any qualified dividend income". Form 8995 line 12 takes
it from Schedule D lines 15 and 16 and Form 1040 line 3a, none of which a
Form 4952 investment income election reduces. A tax unit dependent's gains are
on the dependent's own return.

The YAML cases pin specific returns. This test checks, for random gains,
losses, distributions, dividends, section 1250 and collectibles gain and
elections, in batches of tax units with and without spouses and dependents,
run as vectorized simulations with the dependents' amounts as drawn, with
them set to zero, and with no election:

1. Oracle: `section_199a_net_capital_gain` equals Schedule D's
   max(0, min(line 15, line 16)) plus nonnegative qualified dividends, summed
   from the head's and spouse's inputs in numpy.
2. Election invariance: the election changes neither the gain nor the QBI
   deduction.
3. Dependent invariance: dependents' gains, losses and dividends change
   neither the gain nor the QBI deduction.
4. Cap and floor: the deduction is never negative and never above 20% of
   taxable income less the gain, or the 199A(i) minimum when larger.
5. Gain and deduction ordering: for the same component-derived inputs,
   the 199A gain is nonnegative and at least adjusted net capital gain, so
   its deduction never exceeds the deduction using the former adjusted-gain
   cap, including when the 199A(i) minimum applies.
"""

import numpy as np
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from policyengine_core.periods import period

from policyengine_us import Simulation
from policyengine_us.variables.gov.irs.income.taxable_income.deductions.qualified_business_income_deduction.qualified_business_income_deduction import (
    qualified_business_income_deduction,
)

TOLERANCE = 0.01  # dollars
GAIN_INPUTS = [
    "long_term_capital_gains",
    "short_term_capital_gains",
    "schedule_d_capital_gain_distributions",
    "non_sch_d_capital_gains",
    "qualified_dividend_income",
    "long_term_capital_gains_on_collectibles",
]
HEAD = dict(
    is_tax_unit_head=True, is_tax_unit_spouse=False, is_tax_unit_dependent=False
)
SPOUSE = dict(
    is_tax_unit_head=False, is_tax_unit_spouse=True, is_tax_unit_dependent=False
)
DEPENDENT = dict(
    is_tax_unit_head=False, is_tax_unit_spouse=False, is_tax_unit_dependent=True
)


def _maybe(strategy):
    return st.one_of(st.just(0.0), strategy)


signed = st.integers(-60_000, 120_000).map(float)
positive = st.integers(1, 60_000).map(float)


@st.composite
def person_amounts(draw):
    distributions = draw(_maybe(st.integers(1, 5_000).map(float)))
    # Schedule D line 13 is already inside line 15. The separately stored
    # distribution is a memo component, never an additional gain.
    long_term = draw(_maybe(signed)) + distributions
    return {
        "long_term_capital_gains": long_term,
        "short_term_capital_gains": draw(_maybe(signed)),
        "schedule_d_capital_gain_distributions": distributions,
        "non_sch_d_capital_gains": draw(_maybe(st.integers(1, 5_000).map(float))),
        "qualified_dividend_income": draw(_maybe(positive)),
        # Collectibles gain is part of the long-term gain.
        "long_term_capital_gains_on_collectibles": (
            draw(_maybe(st.integers(0, int(max(0, long_term))).map(float)))
        ),
        "qbid_amount": draw(_maybe(positive)),
        "qualified_business_income": draw(_maybe(positive)),
    }


@st.composite
def tax_units(draw):
    kind = draw(st.sampled_from(["single", "joint", "joint_dependent"]))
    return {
        "head": draw(person_amounts()),
        "spouse": draw(person_amounts()) if kind != "single" else None,
        "dependent": draw(person_amounts()) if kind == "joint_dependent" else None,
        "taxable_income_less_qbid": draw(st.integers(0, 600_000).map(float)),
        "unrecaptured_section_1250_gain": draw(_maybe(positive)),
        "election": draw(_maybe(st.integers(1, 80_000).map(float))),
    }


def _situation(units, year, *, zero_dependents=False, zero_election=False):
    people, tax_units_, households, marital_units = {}, {}, {}, {}
    for i, u in enumerate(units):
        members = []
        for role, flags in (("head", HEAD), ("spouse", SPOUSE)):
            if u[role] is not None:
                name = f"{role}_{i}"
                people[name] = {"age": 45, **flags, **u[role]}
                members.append(name)
        marital_units[f"couple_{i}"] = {"members": list(members)}
        if u["dependent"] is not None:
            name = f"dependent_{i}"
            amounts = dict(u["dependent"])
            if zero_dependents:
                amounts.update({k: 0.0 for k in GAIN_INPUTS})
            people[name] = {"age": 16, **DEPENDENT, **amounts}
            members.append(name)
            marital_units[f"single_{i}"] = {"members": [name]}
        tax_units_[f"tax_unit_{i}"] = {
            "members": members,
            "taxable_income_less_qbid": u["taxable_income_less_qbid"],
            "unrecaptured_section_1250_gain": u["unrecaptured_section_1250_gain"],
        }
        # The election is the head's input.
        people[f"head_{i}"]["investment_income_elected_form_4952"] = (
            0.0 if zero_election else u["election"]
        )
        households[f"household_{i}"] = {"members": members, "state_code": "TX"}

    def by_year(values):
        return {k: (v if k == "members" else {year: v}) for k, v in values.items()}

    return {
        "people": {k: by_year(v) for k, v in people.items()},
        "tax_units": {k: by_year(v) for k, v in tax_units_.items()},
        "households": {k: by_year(v) for k, v in households.items()},
        "marital_units": {k: by_year(v) for k, v in marital_units.items()},
    }


class _AdjustedGainCap:
    """Run the production deduction with only its former gain input restored."""

    def __init__(self, tax_unit):
        self.tax_unit = tax_unit

    def __call__(self, variable, formula_period):
        if variable == "section_199a_net_capital_gain":
            variable = "adjusted_net_capital_gain"
        return self.tax_unit(variable, formula_period)

    def __getattr__(self, name):
        return getattr(self.tax_unit, name)


def _run(units, year, *, compare_legacy=False, **kwargs):
    sim = Simulation(situation=_situation(units, year, **kwargs))
    out = {
        name: np.asarray(sim.calculate(name, year), dtype=float)
        for name in [
            "section_199a_net_capital_gain",
            "qualified_business_income_deduction",
            "taxable_income_less_qbid",
            *GAIN_INPUTS,
        ]
    }
    out["filer"] = ~np.asarray(sim.calculate("is_tax_unit_dependent", year), bool)
    out["unit"] = sim.populations["tax_unit"].members_entity_id
    out["p"] = sim.tax_benefit_system.parameters(year).gov.irs.deductions.qbi
    if compare_legacy:
        out["adjusted_net_capital_gain"] = np.asarray(
            sim.calculate("adjusted_net_capital_gain", year), dtype=float
        )
        # Reuse this simulation's population and parameters. This evaluates
        # the actual deduction formula, including its floor and filer rules,
        # without another model build or a duplicate implementation of QBID.
        out["legacy_qualified_business_income_deduction"] = np.asarray(
            qualified_business_income_deduction.formula(
                _AdjustedGainCap(sim.populations["tax_unit"]),
                period(year),
                sim.tax_benefit_system.parameters,
            ),
            dtype=float,
        )
    return out


def _filer_sum(run, name):
    n = len(run["section_199a_net_capital_gain"])
    return np.bincount(run["unit"], weights=run[name] * run["filer"], minlength=n)


def _check(units, year):
    run = _run(units, year, compare_legacy=True)
    gain = run["section_199a_net_capital_gain"]
    deduction = run["qualified_business_income_deduction"]

    # 1. Oracle: Schedule D lines 15 and 16, and Form 1040 line 3a.
    line_15 = _filer_sum(run, "long_term_capital_gains") + _filer_sum(
        run, "non_sch_d_capital_gains"
    )
    line_16 = line_15 + _filer_sum(run, "short_term_capital_gains")
    dividends = np.maximum(0, _filer_sum(run, "qualified_dividend_income"))
    oracle = np.maximum(0, np.minimum(line_15, line_16)) + dividends
    np.testing.assert_allclose(gain, oracle, atol=TOLERANCE)

    # 2. Election invariance.
    no_election = _run(units, year, zero_election=True)
    for name in [
        "section_199a_net_capital_gain",
        "qualified_business_income_deduction",
    ]:
        np.testing.assert_allclose(
            run[name], no_election[name], atol=TOLERANCE, err_msg=name
        )

    # 3. Dependent invariance.
    no_dependents = _run(units, year, zero_dependents=True)
    for name in [
        "section_199a_net_capital_gain",
        "qualified_business_income_deduction",
    ]:
        np.testing.assert_allclose(
            run[name], no_dependents[name], atol=TOLERANCE, err_msg=name
        )

    # 4. Cap and floor.
    p = run["p"]
    cap = p.max.rate * np.maximum(0, run["taxable_income_less_qbid"] - gain)
    ceiling = cap
    if p.deduction_floor.in_effect:
        # The largest minimum the scale gives.
        ceiling = np.maximum(cap, p.deduction_floor.amount.calc(np.array([1e12]))[0])
    assert (deduction >= -TOLERANCE).all()
    assert (deduction <= ceiling + TOLERANCE).all()

    # 5. Preferential-rate exclusions and elections can only reduce the
    # former gain input. Replacing it cannot increase the deduction, even
    # when the common statutory minimum exceeds either ordinary cap.
    assert (gain >= -TOLERANCE).all()
    assert (gain + TOLERANCE >= run["adjusted_net_capital_gain"]).all()
    assert (
        deduction <= run["legacy_qualified_business_income_deduction"] + TOLERANCE
    ).all()


# Each example is one vectorized batch of tax units.
SETTINGS = dict(
    max_examples=3,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


@settings(**SETTINGS)
@given(st.lists(tax_units(), min_size=10, max_size=40))
def test_section_199a_gain_and_cap_2025(units):
    _check(units, 2025)


@settings(**SETTINGS)
@given(st.lists(tax_units(), min_size=10, max_size=40))
def test_section_199a_gain_and_cap_2026(units):
    # 2026 adds the 199A(i) minimum deduction.
    _check(units, 2026)
