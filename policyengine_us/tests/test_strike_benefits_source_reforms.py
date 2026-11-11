"""State measures that read strike benefits beside federal income, under
reforms that change how federal gross income counts them.

strike_benefits_in_gross_income is the part of strike_benefits that federal
gross income holds, and strike_benefits_excluded_from_gross_income is the
rest. Utah homeowner's and renter's relief, Montana's elderly
homeowner/renter credit and Arizona's property tax credit add the rest to
federal income; Pennsylvania subtracts the part federal gross income holds
and then counts the whole amount in Tax Forgiveness eligibility income.

Invariant: under current law, under a reform that drops
taxable_strike_benefits from gov.irs.gross_income.sources (a federal
exclusion, as the Tax Cut for Striking Workers Act proposes), and under one
that lists the whole strike_benefits instead, every measure counts each
dollar of strike benefits exactly once, and Pennsylvania taxable income
never holds any of it.

One single filer per state, aged 70, with $20,000 of wages and $6,000 of
strike benefits, $1,000 of them a gift.
"""

import pytest
from policyengine_core.periods import instant
from policyengine_core.reforms import Reform

from policyengine_us import Simulation

YEAR = 2025
WAGES = 20_000
STRIKE = 6_000
GIFT = 1_000
STATES = ["UT", "MT", "AZ", "PA"]


def _sources_reform(change):
    class sources_reform(Reform):
        def apply(self):
            def modify(parameters):
                node = parameters.gov.irs.gross_income.sources
                start = instant(f"{YEAR}-01-01")
                node.update(
                    start=start,
                    stop=instant(f"{YEAR}-12-31"),
                    value=change(list(node(start))),
                )
                return parameters

            self.modify_parameters(modify)

    return sources_reform


def _drop(sources):
    return [s for s in sources if s != "taxable_strike_benefits"]


def _swap(sources):
    # Idempotent: the reform's modify function can run more than once.
    kept = [
        s for s in sources if s not in ("taxable_strike_benefits", "strike_benefits")
    ]
    return kept + ["strike_benefits"]


def _situation():
    year = str(YEAR)
    people = {
        state: {
            "age": {year: 70},
            "employment_income": {year: WAGES},
            "strike_benefits": {year: STRIKE},
            "tax_exempt_strike_benefits": {year: GIFT},
            # Keeps the model from computing SSI, which Montana counts.
            "ssi": {year: 0},
        }
        for state in STATES
    }
    return {
        "people": people,
        "tax_units": {f"{s}_unit": {"members": [s]} for s in STATES},
        "households": {
            f"{s}_home": {"members": [s], "state_code": {year: s}} for s in STATES
        },
    }


SCENARIOS = {
    # (reform, part in federal gross income)
    "current law": (None, STRIKE - GIFT),
    "federal exclusion": (_sources_reform(_drop), 0),
    "whole amount in gross income": (_sources_reform(_swap), STRIKE),
}


@pytest.fixture(scope="module", params=list(SCENARIOS))
def scenario(request):
    reform, in_gross_income = SCENARIOS[request.param]
    sim = Simulation(situation=_situation(), reform=reform)
    return sim, in_gross_income


def _person(sim, variable):
    return dict(zip(STATES, sim.calculate(variable, YEAR)))


def test_split_follows_the_gross_income_sources(scenario):
    sim, in_gross_income = scenario
    for state, value in _person(sim, "strike_benefits_in_gross_income").items():
        assert value == pytest.approx(in_gross_income), state
    for state, value in _person(
        sim, "strike_benefits_excluded_from_gross_income"
    ).items():
        assert value == pytest.approx(STRIKE - in_gross_income), state
    for state, value in _person(sim, "irs_gross_income").items():
        assert value == pytest.approx(WAGES + in_gross_income), state


def test_property_relief_counts_strike_benefits_once(scenario):
    sim, _ = scenario
    expected = WAGES + STRIKE
    households = dict(
        zip(STATES, sim.calculate("ut_homeowner_renter_relief_household_income", YEAR))
    )
    assert households["UT"] == pytest.approx(expected)
    households = dict(
        zip(STATES, sim.calculate("az_property_tax_credit_household_income", YEAR))
    )
    assert households["AZ"] == pytest.approx(expected)
    montana = _person(
        sim, "mt_elderly_homeowner_or_renter_credit_gross_household_income"
    )
    assert montana["MT"] == pytest.approx(expected)


def test_pennsylvania_never_taxes_strike_benefits(scenario):
    sim, _ = scenario
    taxable = dict(zip(STATES, sim.calculate("pa_total_taxable_income", YEAR)))
    assert taxable["PA"] == pytest.approx(WAGES)
    eligibility = dict(zip(STATES, sim.calculate("pa_eligibility_income", YEAR)))
    assert eligibility["PA"] == pytest.approx(WAGES + STRIKE)
