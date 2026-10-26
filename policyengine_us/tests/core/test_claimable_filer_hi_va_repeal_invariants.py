"""Hawaii and Virginia exemptions under the contributed repeal of state
dependent exemptions, for filers who can be claimed as a dependent.

The repeal removes the dependent exemptions and nothing else. A filer whom
another taxpayer can claim has no exemption of their own in the baseline:
Hawaii sets it, and the additional exemption for age 65 or over, to zero
(HRS 235-54(a)), and Virginia allows $930 only for each exemption allowable
federally (Va. Code 58.1-322.03(2)(a); IRC 151(d)(2)). Virginia's $800 aged or
blind exemption (58.1-322.03(2)(b)) has no such bar.

For single filers and couples, each filer not claimable, claimable but
unclaimed, claimed, or within the claimant filing exception, with and without
dependents (an exhaustive grid and Hypothesis batches):

1. Dependents only: each output under the repeal equals the baseline output
   for the same return with its dependents removed, and each filer's Virginia
   personal exemption equals the baseline's for that filer on that return.
2. Never above baseline: no output is higher under the repeal than in the
   baseline.
3. No claimable filer gets a Virginia personal exemption under the repeal,
   and no dependent does.
"""

from itertools import product

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import CountryTaxBenefitSystem, Simulation
from policyengine_us.reforms.state_dependent_exemptions.repeal_state_dependent_exemptions import (
    repeal_state_dependent_exemptions,
)
from policyengine_us.tests.core.test_dependent_elsewhere_head_spouse_swap_invariance import (
    adults,
    dependents,
)

STATES = ["HI", "VA"]
YEARS = [2021, 2025, 2026]
OUTPUTS = [
    "hi_regular_exemptions",
    "hi_disabled_exemptions",
    "hi_exemptions",
    "va_personal_exemption",
    "va_aged_blind_exemption",
    "va_total_exemptions",
]
TOLERANCE = 0.01
# (claimable, claimed, claimant filing exception) for each filer.
CLAIM_STATES = {
    "none": (False, False, False),
    "claimable": (True, False, False),
    "claimed": (True, True, False),
    "exception": (True, False, True),
}


@pytest.fixture(scope="module")
def repeal_system():
    # Built once for the module and released when its tests end.
    return CountryTaxBenefitSystem(reform=repeal_state_dependent_exemptions)


def _grid():
    young = {"age": 22, "employment_income": 8_000.0}
    old = {"age": 70, "social_security_retirement": 12_000.0}
    impaired = {"age": 40, "is_blind": True, "is_disabled": True}
    children = [{"age": 4}, {"age": 19, "is_full_time_student": True}]
    filer_sets = [[young], [old], [impaired], [young, old], [old, old]]
    filer_sets += [[young, impaired]]
    units = []
    for state, filers, with_children in product(STATES, filer_sets, [False, True]):
        for states in product(CLAIM_STATES, repeat=len(filers)):
            claimable, claimed, exception = zip(*(CLAIM_STATES[s] for s in states))
            units.append(
                {
                    "state": state,
                    "adults": filers,
                    "dependents": children if with_children else [],
                    "claimable": claimable,
                    "claimed": claimed,
                    "exception": exception,
                }
            )
    return units


@st.composite
def returns(draw):
    filers = draw(st.integers(1, 2))
    claimable = tuple(draw(st.booleans()) for _ in range(filers))
    claimed = tuple(can and draw(st.booleans()) for can in claimable)
    return {
        "state": draw(st.sampled_from(STATES)),
        "adults": [draw(adults()) for _ in range(filers)],
        "dependents": draw(st.lists(dependents(), max_size=2)),
        "claimable": claimable,
        "claimed": claimed,
        "exception": tuple(
            can and not is_claimed and draw(st.booleans())
            for can, is_claimed in zip(claimable, claimed)
        ),
    }


def _situation(units, year, with_dependents=True):
    people = {}
    groups = {
        "tax_units": {},
        "spm_units": {},
        "families": {},
        "marital_units": {},
        "households": {},
    }
    for i, unit in enumerate(units):
        filers = []
        for j, amounts in enumerate(unit["adults"]):
            name = f"filer_{i}_{j}"
            people[name] = {
                **amounts,
                "is_tax_unit_head": j == 0,
                "is_tax_unit_spouse": j == 1,
                "is_tax_unit_dependent": False,
                "claimable_as_dependent_on_another_return": unit["claimable"][j],
                "claimed_as_dependent_on_another_return": unit["claimed"][j],
                "dependent_claimant_filing_exception": unit["exception"][j],
            }
            filers.append(name)
        groups["marital_units"][f"filers_{i}"] = {"members": list(filers)}
        members = list(filers)
        for k, amounts in enumerate(unit["dependents"] if with_dependents else []):
            name = f"dependent_{i}_{k}"
            people[name] = {
                **amounts,
                "is_tax_unit_head": False,
                "is_tax_unit_spouse": False,
                "is_tax_unit_dependent": True,
            }
            members.append(name)
            groups["marital_units"][name] = {"members": [name]}
        for group, prefix in (
            ("tax_units", "tax_unit"),
            ("spm_units", "spm_unit"),
            ("families", "family"),
        ):
            groups[group][f"{prefix}_{i}"] = {"members": members}
        groups["households"][f"household_{i}"] = {
            "members": members,
            "state_code": {year: unit["state"]},
        }
    people = {
        name: {k: {year: v} for k, v in values.items()}
        for name, values in people.items()
    }
    return {"people": people, **groups}


def _calc(sim, name, year):
    return np.asarray(sim.calculate(name, year), dtype=float)


def _describe(units, rows):
    return ", ".join(
        f"{units[i]['state']} filers={len(units[i]['adults'])} "
        f"claimable={units[i]['claimable']} claimed={units[i]['claimed']} "
        f"exception={units[i]['exception']} "
        f"dependents={len(units[i]['dependents'])}"
        for i in rows[:5]
    )


def check_repeal(units, year, system):
    situation = _situation(units, year)
    repeal = Simulation(situation=situation, tax_benefit_system=system)
    baseline = Simulation(situation=situation)
    no_dependents = Simulation(situation=_situation(units, year, False))
    for name in OUTPUTS:
        reformed = _calc(repeal, name, year)
        expected = _calc(no_dependents, name, year)
        current = _calc(baseline, name, year)
        assert np.isfinite(reformed).all(), f"{name} in {year} is not finite"
        differs = np.flatnonzero(np.abs(reformed - expected) > TOLERANCE)
        assert not differs.size, (
            f"{name} in {year} under the repeal differs from the baseline "
            "without dependents: "
            + _describe(units, differs)
            + f"; repeal {reformed[differs[:5]]}, expected {expected[differs[:5]]}"
        )
        rises = np.flatnonzero(reformed > current + TOLERANCE)
        assert not rises.size, (
            f"{name} in {year} is higher under the repeal than in the "
            "baseline: " + _describe(units, rises)
        )
    # Filers keep their order in both situations, so their rows line up.
    filer = _calc(repeal, "is_tax_unit_head_or_spouse", year) > 0
    claimable = _calc(repeal, "claimable_as_dependent_on_another_return", year) > 0
    person = _calc(repeal, "va_personal_exemption_person", year)
    np.testing.assert_allclose(
        person[filer],
        _calc(no_dependents, "va_personal_exemption_person", year),
        atol=TOLERANCE,
        err_msg=f"va_personal_exemption_person in {year}",
    )
    assert not person[~filer].any(), f"a dependent has a VA exemption in {year}"
    assert not person[filer & claimable].any(), (
        f"a claimable filer has a VA personal exemption in {year}"
    )


@pytest.mark.parametrize("year", YEARS)
def test_hi_va_repeal_grid(year, repeal_system):
    check_repeal(_grid(), year, repeal_system)


@settings(
    max_examples=3,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(year=st.sampled_from(YEARS), units=st.lists(returns(), min_size=6, max_size=12))
def test_hi_va_repeal_generated_returns(year, units, repeal_system):
    check_repeal(units, year, repeal_system)
