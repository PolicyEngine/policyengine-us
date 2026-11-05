"""Invariants tying the household and SPM income totals together.

household_net_income and spm_unit_net_income are two views of one family's
cash. Each total keeps its own list of what it adds, in two different files, and
the lists drift: a cash program reaches one total and not the other.

Three invariants hold for every input.

1. The list difference is exactly the documented one. Every program that one
   total counts and the other does not appears below with its reason.
2. A dollar of a cash payment adds a dollar to both totals.
3. For a one-person household, the two net incomes differ only by the SPM's
   subtractions and the items each measure defines differently.

Child care stays out of this file: household_state_benefits and the SPM treat
subsidies differently on purpose, and #9405 and #10569 cover that difference.

YAML pins one household per case. These tests need Hypothesis over amounts and
programs, every state, and a differential check of the two net income formulas.
"""

import re
from pathlib import Path

import numpy as np
import pytest
import yaml
from hypothesis import example, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

PACKAGE = Path(__file__).parent.parent
HOUSEHOLD_LISTS = PACKAGE / "parameters/gov/household"
# household_state_benefits starts in 2023.
YEARS = range(2023, 2027)
TOLERANCE = 0.02

STATES = (
    "AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS "
    "MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY"
).split()

# Counted by household_benefits and left out of spm_unit_benefits on purpose.
HOUSEHOLD_ONLY = {
    # spm_unit_net_income adds these two itself.
    "acp": "added directly in spm_unit_net_income",
    "ebb": "added directly in spm_unit_net_income",
    # Census section 4.3.1 lists the SPM's noncash benefits, and these are not on it.
    "household_head_start_benefits": "not an SPM noncash benefit",
    "household_health_benefits": "not an SPM noncash benefit",
    "commodity_supplemental_food_program": "not an SPM noncash benefit",
    # A lower bill, not a payment.
    "ca_care": "utility bill discount",
    "ca_fera": "utility bill discount",
    "ca_la_ez_save": "utility bill discount",
    "ca_riv_share_payment": "utility bill credit",
    # The SPM values housing assistance at a capped amount of its own.
    "housing_assistance": "spm_unit_capped_housing_subsidy in the SPM",
}

# Counted by spm_unit_benefits and left out of household_benefits on purpose.
SPM_ONLY = {
    "spm_unit_capped_housing_subsidy": "housing_assistance in household_benefits",
    "spm_unit_energy_subsidy": "the SPM's own energy assistance valuation",
    "assigned_aca_ptc": "only under the flat tax reform's deduct_ptc switch",
}

# Sources in the household list that person market_income still lacks.
# #9919 tracks these.
MARKET_HOUSEHOLD_ONLY = {
    "debt_relief",
    "farm_rent_income",
    "partnership_s_corp_income",
}

# Cash payments, with the state that pays each and a year it pays.
CASH_PAYMENTS = [
    ("ak_energy_relief", "person", "AK", 2024),
    ("ak_energy_relief", "person", "AK", 2026),
    ("ak_permanent_fund_dividend", "person", "AK", 2026),
    ("ca_capi", "spm_unit", "CA", 2026),
    ("ca_la_expectant_parent_payment", "person", "CA", 2026),
    ("ca_la_infant_supplement", "household", "CA", 2026),
    ("co_denver_property_tax_relief", "spm_unit", "CO", 2026),
    ("ma_eaedc", "spm_unit", "MA", 2026),
    ("nj_property_tax_relief", "tax_unit", "NJ", 2026),
    ("ny_drive_clean_rebate", "household", "NY", 2026),
]


def block_for(list_name, year):
    raw = yaml.load(
        (HOUSEHOLD_LISTS / f"{list_name}.yaml").read_text(), Loader=yaml.BaseLoader
    )
    dated = sorted(item for item in raw["values"].items() if item[0] <= f"{year}-12-31")
    return set(dated[-1][1]) if dated else set()


def is_child_care(name):
    return "child_care" in name or "ccap" in name


def household_members(year):
    """household_benefits with its nested lists opened up."""
    members = block_for("household_benefits", year)
    assert "household_state_benefits" in members
    assert "household_local_benefits" in members
    nested = block_for("household_state_benefits", year) | block_for(
        "household_local_benefits", year
    )
    return (members | nested) - {"household_state_benefits", "household_local_benefits"}


def spm_members():
    source = PACKAGE / "variables/household/income/spm_unit/spm_unit_benefits.py"
    text = source.read_text()
    listed = set(re.findall(r'^\s+"([a-z0-9_]+)",', text, re.M))
    appended = set(re.findall(r'BENEFITS\.append\("([a-z0-9_]+)"\)', text))
    return listed | appended


def person_market_members():
    source = PACKAGE / "variables/household/income/person/general/market_income.py"
    return set(re.findall(r'^\s+"([a-z0-9_]+)",', source.read_text(), re.M))


@pytest.mark.parametrize("year", YEARS)
def test_benefit_lists_differ_only_where_documented(year):
    household = {name for name in household_members(year) if not is_child_care(name)}
    spm = {name for name in spm_members() if not is_child_care(name)}

    household_extra = household - spm - set(HOUSEHOLD_ONLY)
    spm_extra = spm - household - set(SPM_ONLY)
    assert household_extra == set(), f"{year}: only in household: {household_extra}"
    assert spm_extra == set(), f"{year}: only in SPM: {spm_extra}"


def test_market_income_differs_only_by_the_tracked_sources():
    household = block_for("market_income_sources", 2026)
    assert household - person_market_members() == MARKET_HOUSEHOLD_ONLY
    assert person_market_members() - household == set()


def one_person(state, earnings, year, **variables):
    """A one-person household, with named inputs placed on their entities."""
    groups = {"person": {}, "tax_unit": {}, "spm_unit": {}, "household": {}}
    for name, (entity, value) in variables.items():
        groups[entity][name] = {year: value}
    groups["person"].update(age={year: 40}, employment_income={year: earnings})
    groups["household"]["state_name"] = {year: state}
    members = ["you"]
    return {
        "people": {"you": groups["person"]},
        "tax_units": {"tax_unit": {"members": members, **groups["tax_unit"]}},
        "spm_units": {"spm_unit": {"members": members, **groups["spm_unit"]}},
        "families": {"family": {"members": members}},
        "marital_units": {"marital_unit": {"members": members}},
        "households": {"household": {"members": members, **groups["household"]}},
    }


def total(simulation, names, year):
    return sum(float(simulation.calculate(name, year).sum()) for name in names)


SPM_RESOURCES = ("spm_unit_market_income", "spm_unit_benefits")
HOUSEHOLD_RESOURCES = ("household_market_income", "household_benefits")


@settings(max_examples=20, deadline=None)
@given(
    payment=st.sampled_from(CASH_PAYMENTS),
    amount=st.integers(min_value=1, max_value=30_000),
)
def test_a_dollar_of_cash_adds_a_dollar_to_both_totals(payment, amount):
    name, entity, state, year = payment
    # Earnings this high rule out every means-tested response.
    zero = Simulation(situation=one_person(state, 500_000, year, **{name: (entity, 0)}))
    paid = Simulation(
        situation=one_person(state, 500_000, year, **{name: (entity, amount)})
    )
    for names in (SPM_RESOURCES, HOUSEHOLD_RESOURCES):
        change = total(paid, names, year) - total(zero, names, year)
        assert change == pytest.approx(amount, abs=TOLERANCE), names


# Random states would miss the few that pay these programs, so every state runs.
@pytest.mark.parametrize("state", STATES)
@settings(max_examples=1, deadline=None)
@example(earnings=30_000)
@given(earnings=st.integers(min_value=0, max_value=300_000))
def test_net_incomes_reconcile_for_one_person(state, earnings):
    """A differential test of the two net income formulas.

    spm_unit_net_income subtracts work, medical and child support costs, and it
    leaves out health benefits. household_net_income subtracts health costs and
    counts the benefits and bill discounts listed in HOUSEHOLD_ONLY. Take those
    away and the two totals agree.
    """
    year = 2026
    # Rent makes New Jersey's relief positive, so that payment is under test too.
    simulation = Simulation(
        situation=one_person(state, earnings, year, pre_subsidy_rent=("person", 12_000))
    )

    def value(name):
        return total(simulation, [name], year)

    household_side = (
        value("household_net_income")
        + value("household_health_costs")
        - value("household_health_benefits")
        - sum(value(name) for name in ("ca_care", "ca_fera", "ca_la_ez_save"))
        - value("ca_riv_share_payment")
        - value("commodity_supplemental_food_program")
        - value("household_head_start_benefits")
        - value("housing_assistance")
    )
    spm_side = (
        value("spm_unit_net_income")
        + value("spm_unit_spm_expenses")
        - value("spm_unit_capped_housing_subsidy")
        - value("spm_unit_energy_subsidy")
    )
    assert np.isclose(household_side, spm_side, atol=TOLERANCE)
