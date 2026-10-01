"""Calculating a variable must not change any other variable's value.

policyengine-core returns the cached array itself from ``tax_unit("x",
period)``, so a formula that wrote into it (``x += y``) changed variable
``x`` for every later reader in the same simulation. Five formulas did:

- reforms/crfb/agi_surtax.py wrote the increased base into
  adjusted_gross_income;
- ga_deductions.py subtracted the Georgia adjustment from the federal
  itemized_taxable_income_deductions;
- ut_personal_exemption.py and the Utah dependent exemption reform added
  newborn dependents into ut_total_dependents;
- basic_income_phase_in.py added Social Security into
  tax_unit_earned_income.

Each test below calculates the consumer first, then checks the source
variable against its own value. The last test calculates households of
every kind above in every state with every cached array read-only, so any
formula on that path that writes into a cached array raises at that line.
"""

import numpy as np
import pytest
from policyengine_core.data_storage import InMemoryStorage

from policyengine_us import Simulation
from policyengine_us.reforms.states.ut.dependent_exemption.ut_dependent_exemption_reform import (
    ut_dependent_exemption_reform,
)
from policyengine_us.variables.household.demographic.geographic.state_code import (
    StateCode,
)

YEAR = 2026
ALWAYS = {"2026-01-01.2100-12-31": True}
CRFB_INCREASED_BASE = {
    "gov.contrib.crfb.surtax.in_effect": ALWAYS,
    "gov.contrib.crfb.surtax.increased_base.in_effect": ALWAYS,
}
BASIC_INCOME_WITH_SS_AS_EARNINGS = {
    "gov.contrib.ubi_center.basic_income.amount.person.flat": {
        "2026-01-01.2100-12-31": 12_000
    },
    "gov.contrib.ubi_center.basic_income.phase_in.in_effect": ALWAYS,
    "gov.contrib.ubi_center.basic_income.phase_in.include_ss_benefits_as_earnings": ALWAYS,
}
TERRITORIES = {"GU", "MP", "PW", "PR", "VI", "AA", "AE", "AP"}
STATES = [state.value for state in StateCode if state.value not in TERRITORIES]


def household(state, head, dependents=(), tax_unit=None, prefix=""):
    """One household: a head with ``head`` inputs and optional dependents."""
    people = {f"{prefix}head": {"age": {YEAR: 45}}}
    people[f"{prefix}head"].update({k: {YEAR: v} for k, v in head.items()})
    for index, age in enumerate(dependents):
        people[f"{prefix}dependent_{index}"] = {
            "age": {YEAR: age},
            "is_tax_unit_dependent": {YEAR: True},
        }
    members = list(people)
    return {
        "people": people,
        "tax_units": {
            f"{prefix}tax_unit": {
                "members": members,
                **{k: {YEAR: v} for k, v in (tax_unit or {}).items()},
            }
        },
        "spm_units": {f"{prefix}spm_unit": {"members": members}},
        "households": {
            f"{prefix}household": {
                "members": members,
                "state_name": {YEAR: state},
            }
        },
    }


def calculate(situation, variable, reform=None):
    return Simulation(situation=situation, reform=reform).calculate(variable, YEAR)


def test_crfb_surtax_increased_base_leaves_agi_unchanged():
    situation = household(
        "TX",
        {"employment_income": 400_000, "tax_exempt_interest_income": 50_000},
    )
    simulation = Simulation(situation=situation, reform=CRFB_INCREASED_BASE)
    simulation.calculate("income_tax", YEAR)
    assert simulation.calculate("adjusted_gross_income", YEAR)[0] == 400_000
    # The surtax base still includes the tax-exempt interest:
    # 1% of ($450,000 - $100,000).
    assert simulation.calculate("agi_surtax", YEAR)[0] == pytest.approx(3_500)


def test_crfb_surtax_increased_base_leaves_state_income_tax_unchanged():
    # New York's tax starts from federal AGI; the surtax does not change it.
    situation = household(
        "NY",
        {
            "employment_income": 150_000,
            "traditional_401k_contributions": 20_000,
            "health_insurance_premiums": 6_000,
        },
    )
    simulation = Simulation(situation=situation, reform=CRFB_INCREASED_BASE)
    simulation.calculate("household_net_income", YEAR)
    assert simulation.calculate("agi_surtax", YEAR)[0] > 0
    assert simulation.calculate("state_income_tax", YEAR)[0] == pytest.approx(
        calculate(situation, "state_income_tax")[0]
    )


def test_ga_deductions_leave_federal_itemized_deductions_unchanged():
    situation = household(
        "GA",
        {
            "employment_income": 150_000,
            "mortgage_interest": 25_000,
            "charitable_cash_donations": 10_000,
            "real_estate_taxes": 8_000,
        },
        tax_unit={"ga_itemized_deductions_adjustment": 4_000},
    )
    federal_itemized = calculate(situation, "itemized_taxable_income_deductions")[0]
    simulation = Simulation(situation=situation)
    simulation.calculate("household_net_income", YEAR)
    assert simulation.calculate("tax_unit_itemizes", YEAR)[0]
    assert simulation.calculate("itemized_taxable_income_deductions", YEAR)[
        0
    ] == pytest.approx(federal_itemized)
    assert simulation.calculate("ga_deductions", YEAR)[0] == pytest.approx(
        federal_itemized - 4_000
    )


UTAH_NEWBORN_AND_CHILD = household(
    "UT", {"employment_income": 60_000}, dependents=(0, 5)
)


@pytest.mark.parametrize(
    "reform",
    [None, ut_dependent_exemption_reform],
    ids=["baseline", "dependent_exemption_reform_not_in_effect"],
)
def test_ut_personal_exemption_leaves_total_dependents_unchanged(reform):
    simulation = Simulation(situation=UTAH_NEWBORN_AND_CHILD, reform=reform)
    simulation.calculate("household_net_income", YEAR)
    # Two dependents; the newborn earns a second exemption without
    # becoming a third dependent.
    assert simulation.calculate("ut_total_dependents", YEAR)[0] == 2
    p = simulation.tax_benefit_system.parameters(
        YEAR
    ).gov.states.ut.tax.income.credits.taxpayer
    assert simulation.calculate("ut_personal_exemption", YEAR)[0] == pytest.approx(
        3 * p.personal_exemption
    )


def test_basic_income_phase_in_leaves_earned_income_unchanged():
    situation = household(
        "TX",
        {
            "age": 70,
            "employment_income": 10_000,
            "social_security_retirement": 20_000,
        },
    )
    simulation = Simulation(
        situation=situation, reform=BASIC_INCOME_WITH_SS_AS_EARNINGS
    )
    simulation.calculate("household_net_income", YEAR)
    assert simulation.calculate("tax_unit_earned_income", YEAR)[0] == 10_000
    assert simulation.calculate("basic_income_phase_in", YEAR)[0] == 30_000


def every_state():
    """Each household above, plus a retiree, in every state and DC."""
    situation = {"people": {}, "tax_units": {}, "spm_units": {}, "households": {}}
    kinds = {
        "itemizer": dict(
            head={
                "employment_income": 150_000,
                "traditional_401k_contributions": 20_000,
                "health_insurance_premiums": 6_000,
                "tax_exempt_interest_income": 5_000,
                "mortgage_interest": 25_000,
                "charitable_cash_donations": 10_000,
                "real_estate_taxes": 8_000,
            },
            tax_unit={"ga_itemized_deductions_adjustment": 4_000},
        ),
        "newborn": dict(head={"employment_income": 60_000}, dependents=(0, 5)),
        "retiree": dict(
            head={
                "age": 70,
                "employment_income": 10_000,
                "social_security_retirement": 20_000,
            }
        ),
    }
    for state in STATES:
        for kind, inputs in kinds.items():
            one = household(state, prefix=f"{state}_{kind}_", **inputs)
            for group, members in one.items():
                situation[group].update(members)
    return situation


@pytest.fixture
def read_only_cache(monkeypatch):
    """Make every array a simulation stores read-only as it is stored."""
    put = InMemoryStorage.put

    def read_only_put(self, value, period, branch_name="default"):
        if isinstance(value, np.ndarray):
            value.flags.writeable = False
        return put(self, value, period, branch_name)

    monkeypatch.setattr(InMemoryStorage, "put", read_only_put)


@pytest.mark.parametrize(
    "reform",
    [
        None,
        CRFB_INCREASED_BASE,
        ut_dependent_exemption_reform,
        BASIC_INCOME_WITH_SS_AS_EARNINGS,
    ],
    ids=["baseline", "crfb_surtax", "ut_dependent_exemption", "basic_income"],
)
def test_no_formula_writes_into_a_cached_array(read_only_cache, reform):
    simulation = Simulation(situation=every_state(), reform=reform)
    for variable in ["household_net_income", "income_tax", "state_income_tax"]:
        assert np.isfinite(simulation.calculate(variable, YEAR)).all()
