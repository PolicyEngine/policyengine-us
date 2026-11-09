"""Invariants tying the household and SPM income totals together.

household_net_income and spm_unit_net_income are two views of one family's
cash. Each total keeps its own list of what it adds, in two different files, and
the lists drift: a cash program reaches one total and not the other.

Six invariants hold for every input.

1. The list difference is exactly the documented one. Every program that one
   total counts and the other does not appears below with its reason.
2. A dollar of a cash payment adds a dollar to both totals.
3. For a one-person household, the two net incomes differ only by the SPM's
   subtractions and the items each measure defines differently.
4. Every source of federal gross income reaches SPM resources, or appears below
   with the reason the SPM leaves it out. spm_unit_taxes subtracts the tax on
   all of them, so a source missing from resources costs the family the tax
   without the income (#9919).
5. A dollar of market income, or of a loss, moves both totals by a dollar, and
   cash income never lowers the SPM net income of a family with no
   means-tested benefits to lose.
6. The head and spouse together hold a tax unit's whole Form 4797 amount, with
   its sign, and gross income holds its positive part.

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

# Sources in the household list that person market_income leaves out on purpose.
MARKET_HOUSEHOLD_ONLY = {
    "debt_relief": "discharged debt is not cash, and Census money income leaves it out",
}

GROSS_INCOME_SOURCES = PACKAGE / "parameters/gov/irs/gross_income/sources.yaml"

# Each source of federal gross income, and the market_income or
# spm_unit_benefits member that counts its cash in SPM resources.
GROSS_INCOME_IN_RESOURCES = {
    "irs_employment_income": "employment_income",
    # employment_income holds these benefits: irs_employment_income subtracts
    # them, and the part above the IRC 129 exclusion returns here.
    "taxable_dependent_care_benefits": "employment_income",
    "self_employment_income": "self_employment_income",
    "sstb_self_employment_income": "sstb_self_employment_income",
    "partnership_s_corp_income": "partnership_s_corp_income",
    "farm_operations_income": "farm_operations_income",
    "farm_rent_income": "farm_rent_income",
    "other_net_gain_gross_income": "other_net_gain_person",
    "capital_gains": "capital_gains",
    "non_sch_d_capital_gains": "non_sch_d_capital_gains",
    "taxable_interest_income": "interest_income",
    "rental_income": "rental_income",
    "dividend_income": "dividend_income",
    "taxable_pension_income": "pension_income",
    "taxable_disability_benefits": "disability_benefits",
    "estate_income": "estate_income",
    "taxable_unemployment_compensation": "total_unemployment_compensation",
    "taxable_social_security": "social_security",
    "illicit_income": "illicit_income",
    "taxable_retirement_distributions": "retirement_distributions",
    "miscellaneous_income": "miscellaneous_income",
    "ak_permanent_fund_dividend": "ak_permanent_fund_dividend",
    "taxable_ak_energy_relief": "ak_energy_relief",
    "taxable_alimony_income": "alimony_income",
    "military_retirement_income": "military_retirement_income",
}

# Sources of federal gross income that SPM resources leave out, and why. The
# SPM still subtracts the tax on them: the family owes it either way.
GROSS_INCOME_OUTSIDE_RESOURCES = {
    "debt_relief": "discharged debt is not cash the family receives",
    "taxable_roth_conversions": "moves savings between retirement accounts, "
    "and is not cash available for spending",
    "salt_refund_income": "returns state and local tax paid for an earlier "
    "year, and the SPM subtracts each year's tax as owed, not as paid",
}

# Market income inputs: the entity each sits on, and whether it can be a loss.
MARKET_SOURCES = [
    ("partnership_income", "person", True),
    ("s_corp_income", "person", True),
    ("farm_rent_income", "person", True),
    ("non_sch_d_capital_gains", "person", False),
    ("other_net_gain", "tax_unit", True),
    ("disability_benefits", "person", False),
]

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


def test_market_income_differs_only_where_documented():
    household = block_for("market_income_sources", 2026)
    assert household - person_market_members() == set(MARKET_HOUSEHOLD_ONLY)
    assert person_market_members() - household == set()


def gross_income_sources():
    """Every source in any year block of the federal gross income list."""
    raw = yaml.load(GROSS_INCOME_SOURCES.read_text(), Loader=yaml.BaseLoader)
    return {name for block in raw["values"].values() for name in block}


def test_every_gross_income_source_reaches_spm_resources_or_is_documented():
    sources = gross_income_sources()
    counted = set(GROSS_INCOME_IN_RESOURCES)
    left_out = set(GROSS_INCOME_OUTSIDE_RESOURCES)
    assert not counted & left_out
    unmapped = sources - counted - left_out
    assert unmapped == set(), (
        f"Gross income sources with no SPM treatment: {sorted(unmapped)}. Map "
        "each to the resource that counts its cash, or document why the SPM "
        "leaves it out."
    )
    assert (counted | left_out) - sources == set(), "stale entries above"

    resources = person_market_members() | spm_members()
    uncounted = {
        source: resource
        for source, resource in GROSS_INCOME_IN_RESOURCES.items()
        if resource not in resources
    }
    assert uncounted == {}, f"mapped to a variable SPM resources lack: {uncounted}"
    assert not left_out & resources


def market_situation(name, entity, amount, year=2026, state="TX"):
    # Earnings this high rule out every means-tested response.
    return one_person(state, 500_000, year, **{name: (entity, amount)})


@settings(max_examples=25, deadline=None)
@given(
    source=st.sampled_from(MARKET_SOURCES),
    magnitude=st.integers(min_value=1, max_value=200_000),
    loss=st.booleans(),
)
@example(source=MARKET_SOURCES[0], magnitude=287_010, loss=False)
@example(source=MARKET_SOURCES[0], magnitude=40_000, loss=True)
def test_market_income_moves_both_totals_dollar_for_dollar(source, magnitude, loss):
    name, entity, can_be_loss = source
    amount = -magnitude if loss and can_be_loss else magnitude
    zero = Simulation(situation=market_situation(name, entity, 0))
    paid = Simulation(situation=market_situation(name, entity, amount))
    for names in (("spm_unit_market_income",), ("household_market_income",)):
        change = total(paid, names, 2026) - total(zero, names, 2026)
        assert change == pytest.approx(amount, abs=TOLERANCE), names


@settings(max_examples=25, deadline=None)
@given(
    source=st.sampled_from(MARKET_SOURCES),
    amount=st.integers(min_value=1, max_value=200_000),
    state=st.sampled_from(STATES),
)
@example(source=MARKET_SOURCES[0], amount=287_010, state="TN")
def test_cash_income_never_lowers_spm_net_income(source, amount, state):
    """The tax on a source never exceeds the source in SPM resources.

    Before #9919 the SPM subtracted the tax on partnership income without
    counting the income, so this net change was negative.
    """
    name, entity, _ = source
    zero = Simulation(situation=market_situation(name, entity, 0, state=state))
    paid = Simulation(situation=market_situation(name, entity, amount, state=state))
    change = total(paid, ["spm_unit_net_income"], 2026) - total(
        zero, ["spm_unit_net_income"], 2026
    )
    assert -TOLERANCE <= change <= amount + TOLERANCE


@settings(max_examples=10, deadline=None)
@given(
    amount=st.integers(min_value=-200_000, max_value=200_000),
    has_spouse=st.booleans(),
    children=st.integers(min_value=0, max_value=2),
)
@example(amount=-6_000, has_spouse=True, children=1)
@example(amount=10_000, has_spouse=True, children=0)
def test_head_and_spouse_hold_the_whole_form_4797_amount(amount, has_spouse, children):
    year = 2026
    people = {"head": {"age": {year: 45}, "is_tax_unit_head": {year: True}}}
    adults = ["head"]
    if has_spouse:
        people["spouse"] = {"age": {year: 43}, "is_tax_unit_spouse": {year: True}}
        adults.append("spouse")
    kids = [f"child_{index}" for index in range(children)]
    for kid in kids:
        people[kid] = {"age": {year: 8}, "is_tax_unit_dependent": {year: True}}
    members = adults + kids
    simulation = Simulation(
        situation={
            "people": people,
            "tax_units": {
                "tax_unit": {"members": members, "other_net_gain": {year: amount}}
            },
            "spm_units": {"spm_unit": {"members": members}},
            "families": {"family": {"members": members}},
            "marital_units": {
                "adults": {"members": adults},
                **{kid: {"members": [kid]} for kid in kids},
            },
            "households": {
                "household": {"members": members, "state_name": {year: "TX"}}
            },
        }
    )
    shares = simulation.calculate("other_net_gain_person", year)
    gross = simulation.calculate("other_net_gain_gross_income", year)
    expected = [amount / len(adults)] * len(adults) + [0] * len(kids)
    assert list(shares) == pytest.approx(expected, abs=TOLERANCE)
    assert list(gross) == pytest.approx([max(0, x) for x in expected], abs=TOLERANCE)
    assert total(simulation, ["spm_unit_market_income"], year) == pytest.approx(
        amount, abs=TOLERANCE
    )


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
