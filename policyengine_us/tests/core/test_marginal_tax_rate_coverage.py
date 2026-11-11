"""Invariants of which people get a simulated marginal tax rate.

The marginal tax rate variables run one branch simulation per adult rank, from
1 to simulation.marginal_tax_rate_adults, perturbing the adult whose
adult_earnings_index (rank by market income within the household) equals that
rank. Everyone else keeps a placeholder of zero. marginal_tax_rate_computed
flags the simulated people, and cliff_evaluated must agree with it because the
cliff gap is derived from marginal_tax_rate.

Every household in a grid of adult counts, earnings orders, ties, negative
market income, teen earners and children shares one simulation per cap, and is
checked against that rule, restated here without adult_earnings_index:

1. Each household flags min(cap, adults) people, all adults, and every flagged
   adult has at least the market income of every unflagged adult.
2. cliff_evaluated equals marginal_tax_rate_computed.
3. Every marginal tax rate variable is exactly zero wherever the flag is false.
4. Raising the cap only adds people: anyone flagged under a lower cap keeps the
   same flag and the same marginal tax rates under a higher one. This holds with
   behavioral responses off, as here; with labor supply responses on, the cap
   changes measured marginal tax rates and so earnings and ranks.
"""

from functools import cache
from itertools import product

import numpy as np
import pytest
from policyengine_core.reforms import Reform

from policyengine_us import Simulation

YEAR = 2024
CAP = "simulation.marginal_tax_rate_adults"
# One variable per code path: the net income loop, its health-benefit copy, and
# the component helper shared by the federal, state and FICA variables.
MTR_VARIABLES = (
    "marginal_tax_rate",
    "marginal_tax_rate_including_health_benefits",
    "federal_marginal_tax_rate",
)
# Employment income per adult; a negative entry is a self-employment loss, which
# makes that adult's market income negative.
ADULT_EARNINGS = (
    (0,),
    (40_000,),
    (80_000, 0),
    (0, 80_000),
    (50_000, 50_000),
    (0, 0, 0),
    (30_000, 90_000, 60_000),
    (20_000, 0, 20_000, 70_000),
    (10_000, 45_000, 0, 45_000, 120_000),
    (-20_000, 30_000),
    (10_000, -5_000, 0, 60_000),
)
TEEN_EARNINGS = (None, 0, 8_000)
HAS_CHILD = (False, True)


def _situation():
    people, tax_units, spm_units, households = {}, {}, {}, {}
    shapes = product(ADULT_EARNINGS, TEEN_EARNINGS, HAS_CHILD)
    for h, (adults, teen, child) in enumerate(shapes):
        members = []
        for a, earnings in enumerate(adults):
            name = f"h{h}_adult{a}"
            income = "employment_income" if earnings >= 0 else "self_employment_income"
            people[name] = {"age": {YEAR: 25 + 7 * a}, income: {YEAR: earnings}}
            tax_units[f"{name}_tax_unit"] = {"members": [name]}
            members.append(name)
        dependents = []
        if teen is not None:
            dependents.append(f"h{h}_teen")
            people[f"h{h}_teen"] = {
                "age": {YEAR: 16},
                "employment_income": {YEAR: teen},
            }
        if child:
            dependents.append(f"h{h}_child")
            people[f"h{h}_child"] = {"age": {YEAR: 6}}
        tax_units[f"h{h}_adult0_tax_unit"]["members"] += dependents
        members += dependents
        spm_units[f"h{h}_spm_unit"] = {"members": members}
        households[f"h{h}"] = {"members": members, "state_code": {YEAR: "TX"}}
    return {
        "people": people,
        "tax_units": tax_units,
        "spm_units": spm_units,
        "households": households,
    }


def _simulation(cap):
    return Simulation(
        situation=_situation(),
        reform=Reform.from_dict({CAP: {str(YEAR): cap}}, country_id="us"),
    )


def _calc(simulation, variable):
    return np.asarray(simulation.calculate(variable, YEAR))


@pytest.fixture(scope="module")
def results_for_cap():
    # The flag and rate checks use identical situations. Keep only read-only
    # output snapshots; each cap still gets its own simulation and reform.
    @cache
    def calculate(cap):
        simulation = _simulation(cap)
        results = {
            variable: _calc(simulation, variable)
            for variable in ("marginal_tax_rate_computed", "cliff_evaluated")
        }
        if cap == 0:
            results.update(
                household_id=simulation.populations["household"].members_entity_id,
                is_adult=_calc(simulation, "is_adult").astype(bool),
                market_income=_calc(simulation, "market_income"),
            )
        if cap in (2, 3):
            results.update(
                (variable, _calc(simulation, variable)) for variable in MTR_VARIABLES
            )
        for variable, values in results.items():
            results[variable] = values.copy()
            results[variable].setflags(write=False)
        return results

    return calculate


@pytest.fixture(scope="module")
def households(results_for_cap):
    return results_for_cap(0)


@pytest.mark.parametrize("cap", [0, 1, 2, 3, 5])
def test_flag_selects_the_top_earning_adults(households, results_for_cap, cap):
    results = results_for_cap(cap)
    flag = results["marginal_tax_rate_computed"].astype(bool)
    assert np.array_equal(results["cliff_evaluated"].astype(bool), flag)
    assert not flag[~households["is_adult"]].any()
    for household_id in np.unique(households["household_id"]):
        in_household = households["household_id"] == household_id
        adults = in_household & households["is_adult"]
        flagged = in_household & flag
        assert flagged.sum() == min(cap, adults.sum())
        unflagged_adults = adults & ~flag
        if flagged.any() and unflagged_adults.any():
            income = households["market_income"]
            assert income[flagged].min() >= income[unflagged_adults].max()


@pytest.fixture(scope="module")
def mtr_by_cap(results_for_cap):
    return {cap: results_for_cap(cap) for cap in (2, 3)}


@pytest.mark.parametrize("variable", MTR_VARIABLES)
def test_unsimulated_people_get_a_placeholder_zero(mtr_by_cap, variable):
    for results in mtr_by_cap.values():
        flag = results["marginal_tax_rate_computed"].astype(bool)
        assert (results[variable][~flag] == 0).all()


@pytest.mark.parametrize("variable", MTR_VARIABLES)
def test_raising_the_cap_only_adds_people(mtr_by_cap, variable):
    lower, higher = mtr_by_cap[2], mtr_by_cap[3]
    lower_flag = lower["marginal_tax_rate_computed"].astype(bool)
    higher_flag = higher["marginal_tax_rate_computed"].astype(bool)
    assert (higher_flag[lower_flag]).all()
    assert higher_flag.sum() > lower_flag.sum()
    assert np.array_equal(lower[variable][lower_flag], higher[variable][lower_flag])


# Three single roommates in Texas in 2024, each filing alone. Taxable income is
# wages less the $14,600 standard deduction ($75,400, $45,400, $15,400), so a
# $1,000 raise is taxed at 22%, 12% and 12%, plus 7.65% employee payroll tax.
# Nobody crosses a bracket or payroll threshold, and Texas has no income tax.
ROOMMATE_WAGES = (90_000, 60_000, 30_000)
ROOMMATE_RATES = {
    "marginal_tax_rate": (0.2965, 0.1965, 0.1965),
    "federal_marginal_tax_rate": (0.22, 0.12, 0.12),
    "fica_marginal_tax_rate": (0.0765, 0.0765, 0.0765),
    "state_marginal_tax_rate": (0, 0, 0),
}


@pytest.mark.parametrize("cap", [2, 3])
def test_roommates_match_hand_computed_rates(cap):
    names = [f"roommate{i}" for i in range(len(ROOMMATE_WAGES))]
    situation = {
        "people": {
            name: {"age": {YEAR: 40 - 5 * i}, "employment_income": {YEAR: wages}}
            for i, (name, wages) in enumerate(zip(names, ROOMMATE_WAGES))
        },
        "tax_units": {f"{name}_tax_unit": {"members": [name]} for name in names},
        "spm_units": {f"{name}_spm_unit": {"members": [name]} for name in names},
        "households": {"home": {"members": names, "state_code": {YEAR: "TX"}}},
    }
    simulation = Simulation(
        situation=situation,
        reform=Reform.from_dict({CAP: {str(YEAR): cap}}, country_id="us"),
    )
    simulated = np.arange(len(names)) < cap
    assert np.array_equal(
        _calc(simulation, "marginal_tax_rate_computed").astype(bool), simulated
    )
    for variable, rates in ROOMMATE_RATES.items():
        expected = np.where(simulated, rates, 0)
        assert np.allclose(_calc(simulation, variable), expected, atol=1e-4)
