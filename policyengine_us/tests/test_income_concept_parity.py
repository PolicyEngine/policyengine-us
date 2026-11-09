"""Invariants for Census money income and the CBO household income measures.

census_money_income sums the 18 sources of Census Current Population Reports
P60-200, Appendix A, one list each in gov.household.census_money_income_sources.
CBO's measures sum their own lists in gov.household (cbo_*). Both sit beside
household_benefits and market_income_sources, and lists kept in separate files
drift: a program added to household_benefits reaches neither concept, or a
source lands in two CBO categories and counts twice.

These tests check five invariants in each year from 2022, the first year of
household_benefits. The first two read the lists. The last three hold each
source as an input, because a program's own formula responds to income: a
dollar of wages can change a benefit.

1. Every source that any of these lists counts appears in each concept, or in
   that concept's documented exclusions below, with the reason.
2. No source counts twice: no list repeats a variable, no variable sits under
   two Census sources, the CBO categories are disjoint, CBO adds nothing
   household market income already holds, and neither concept counts a variable
   beside another that reaches it through `adds`.
3. A dollar of a listed source adds a dollar to its concept. A person's Census
   money income gains the dollar, or an equal share of a dollar paid to a
   group, and the family and household totals gain the dollar. The CBO
   category that lists a source gains the dollar and the others do not.
   Retirement account distributions count only from the age Census counts
   them.
4. A dollar of a source a concept leaves out moves that concept not at all.
5. Family and household totals sum their members, census_money_income matches
   an independent allocation of each source, and Census household money income
   reconciles with household market income and household benefits through the
   documented differences, in every state.

YAML pins one household per case. These tests run every listed and excluded
source at once, with Hypothesis over amounts and household sizes.
"""

import functools
import itertools
import re
from collections import Counter
from pathlib import Path

import numpy as np
import pytest
import yaml
from hypothesis import example, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

PACKAGE = Path(__file__).parent.parent
HOUSEHOLD_LISTS = PACKAGE / "parameters/gov/household"
CENSUS_LISTS = HOUSEHOLD_LISTS / "census_money_income_sources"
MARKET_INCOME_SOURCES = HOUSEHOLD_LISTS / "market_income_sources.yaml"
# household_benefits begins in 2022.
YEARS = range(2022, 2027)
TOLERANCE = 0.05
# Census household money income adds about 100 float32 terms, so the
# reconciliation allows for their rounding.
RECONCILIATION_TOLERANCE = 1.0

STATES = (
    "AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS "
    "MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY"
).split()

# Appendix A's 18 sources, in its order (pages A-1 and A-2).
CENSUS_SOURCES = (
    "earnings",
    "unemployment_compensation",
    "workers_compensation",
    "social_security",
    "supplemental_security_income",
    "public_assistance",
    "veterans_payments",
    "survivor_benefits",
    "disability_benefits",
    "pension_or_retirement_income",
    "interest",
    "dividends",
    "rents_royalties_estates_and_trusts",
    "educational_assistance",
    "alimony",
    "child_support",
    "financial_assistance",
    "other_income",
)

# Money income leaves out noncash benefits (Appendix A, page A-2) and these
# receipts (page A-3): capital gains, bank withdrawals, borrowing, tax refunds,
# gifts, and lump-sum inheritances or insurance payments.
NONCASH = "a noncash benefit"
HEALTH = "health coverage, a noncash benefit"
EMPLOYER = "an employer payment, not money the worker receives"
DISCOUNT = "lowers a bill, not money received"
REBATE = "lowers the price of a purchase, not money received"
PROPERTY_TAX_RELIEF = (
    "property tax relief, a tax refund for homeowners, which Appendix A leaves "
    "out; this list treats renters' relief the same way"
)
CENSUS_EXCLUDED = {
    # Market income.
    "capital_gains": "capital gains",
    "non_sch_d_capital_gains": "capital gains",
    "other_net_gain_person": "gains on sales of business property (Form 4797)",
    "debt_relief": "discharged debt, not a receipt of money",
    "illicit_income": "income from bribes and other illegal activity, which "
    "neither Appendix A nor the survey's subject definitions mention (a "
    "judgment call: other income could be read to take it)",
    "miscellaneous_income": "the default data mixes Census other income "
    "(source 18) on survey records with Form 4797 business property gains and "
    "losses (left out, page A-3) on tax records (microcosm#393), and the model "
    "cannot separate them",
    # CBO's employer-side and imputed components.
    "employer_sponsored_insurance_premiums": EMPLOYER,
    "employer_social_security_tax": EMPLOYER,
    "employer_medicare_tax": EMPLOYER,
    "employer_federal_unemployment_tax": EMPLOYER,
    "cbo_corporate_income_tax": "CBO's allocation of corporate income tax, "
    "not a receipt",
    # Health coverage.
    "medicaid": HEALTH,
    "medicaid_cost": HEALTH,
    "chip": HEALTH,
    "msp_cost": HEALTH,
    "medicare_cost": HEALTH,
    "assigned_aca_ptc": "a tax credit paid to the insurer",
    "assigned_ca_premium_subsidy": HEALTH,
    "assigned_co_premium_assistance": HEALTH,
    "assigned_nm_premium_assistance": HEALTH,
    "basic_health_program": HEALTH,
    "co_omnisalud": HEALTH,
    "ct_covered_connecticut": HEALTH,
    "ma_connector_care": HEALTH,
    "md_premium_assistance": HEALTH,
    "nj_njhps": HEALTH,
    "or_healthier_oregon_cost": HEALTH,
    "vt_premium_assistance": HEALTH,
    "wa_cascade_care_savings": HEALTH,
    # Food, housing, energy, child care and early education.
    "snap": NONCASH,
    "wic": NONCASH,
    "free_school_meals": NONCASH,
    "reduced_price_school_meals": NONCASH,
    "commodity_supplemental_food_program": NONCASH,
    "housing_assistance": NONCASH,
    "spm_unit_energy_subsidy": NONCASH,
    "household_child_care_subsidies": NONCASH,
    "head_start": NONCASH,
    "early_head_start": NONCASH,
    # Discounts and rebates.
    "acp": DISCOUNT,
    "ebb": DISCOUNT,
    "ca_care": DISCOUNT,
    "ca_fera": DISCOUNT,
    "ca_la_ez_save": DISCOUNT,
    "ca_riv_share_payment": DISCOUNT,
    "ca_cvrp": REBATE,
    "high_efficiency_electric_home_rebate": REBATE,
    "residential_efficiency_electrification_rebate": REBATE,
    "ny_drive_clean_rebate": REBATE,
    # Tax relief.
    "nj_property_tax_relief": PROPERTY_TAX_RELIEF,
    "co_denver_property_tax_relief": PROPERTY_TAX_RELIEF,
    "state_property_tax_refunds": PROPERTY_TAX_RELIEF,
}

# CBO's measures (The Distribution of Household Income in 2021, Appendix D)
# count market income, four social insurance programs, listed means-tested
# programs, and federal taxes net of refundable credits.
OUTSIDE_CBO = "not in market income or a program CBO lists"
CBO_EXCLUDED = {
    "veterans_benefits": "CBO's categories have not named veterans' benefits "
    "since its report on 2014, published in March 2018; its working paper "
    "2017-09 counted them as means-tested transfers",
    "pfml_benefits": "state paid leave insurance: CBO's social insurance is "
    "Social Security, Medicare, unemployment insurance and workers' "
    "compensation",
    "census_retirement_distributions": "Census's age-limited view of "
    "retirement_distributions, which CBO's market income counts in full",
    "educational_assistance": "Pell Grants and other government aid beside "
    "private scholarships (IPUMS INCEDUC), which the model does not split: "
    "CBO's other income covers only nongovernmental sources, and its transfer "
    "lists name no education grants",
    # cbo_market_income_subtractions removes these two from household market
    # income.
    "gi_cash_assistance": "guaranteed income pilot payments, which CBO's lists "
    "do not name",
    "ak_permanent_fund_dividend": "Alaska's dividend to eligible residents, "
    "a government payment outside CBO's categories",
    "ak_energy_relief": "Alaska's energy relief, paid with the dividend, "
    "outside CBO's categories",
    "basic_income": "a proposed universal payment (contributed reform), "
    "outside CBO's categories",
    "trump_dividend": "a proposed payment (contributed reform), outside CBO's "
    "categories",
    "acp": OUTSIDE_CBO,
    "ebb": OUTSIDE_CBO,
    "ca_care": OUTSIDE_CBO,
    "ca_fera": OUTSIDE_CBO,
    "ca_la_ez_save": OUTSIDE_CBO,
    "ca_riv_share_payment": OUTSIDE_CBO,
    "ca_cvrp": OUTSIDE_CBO,
    "high_efficiency_electric_home_rebate": OUTSIDE_CBO,
    "residential_efficiency_electrification_rebate": OUTSIDE_CBO,
    "ny_drive_clean_rebate": OUTSIDE_CBO,
    "ca_la_expectant_parent_payment": OUTSIDE_CBO,
    "ca_la_infant_supplement": OUTSIDE_CBO,
    "co_denver_property_tax_relief": OUTSIDE_CBO,
    "nj_property_tax_relief": OUTSIDE_CBO,
    "state_property_tax_refunds": OUTSIDE_CBO,
    "commodity_supplemental_food_program": OUTSIDE_CBO,
    "head_start": OUTSIDE_CBO,
    "early_head_start": OUTSIDE_CBO,
    "household_child_care_subsidies": OUTSIDE_CBO,
    "assigned_ca_premium_subsidy": OUTSIDE_CBO,
    "assigned_co_premium_assistance": OUTSIDE_CBO,
    "assigned_nm_premium_assistance": OUTSIDE_CBO,
    "basic_health_program": OUTSIDE_CBO,
    "co_omnisalud": OUTSIDE_CBO,
    "ct_covered_connecticut": OUTSIDE_CBO,
    "ma_connector_care": OUTSIDE_CBO,
    "md_premium_assistance": OUTSIDE_CBO,
    "nj_njhps": OUTSIDE_CBO,
    "or_healthier_oregon_cost": OUTSIDE_CBO,
    "vt_premium_assistance": OUTSIDE_CBO,
    "wa_cascade_care_savings": OUTSIDE_CBO,
}

# CBO's income totals, before and after transfers.
CBO_INCOMES = (
    "cbo_household_market_income",
    "cbo_household_social_insurance_benefits",
    "cbo_household_means_tested_transfers",
)

# Sources Census counts through the variables they add, because Appendix A
# puts the parts under different sources: military retirement pay under
# pension or retirement income, military survivor annuities under survivor
# benefits.
CENSUS_COUNTED_AS = {
    "military_retirement_income": (
        "military_retirement_pay",
        "military_retirement_pay_survivors",
    ),
}

# Sources Census counts only in part, through the variable that applies the
# limit: since the redesigned processing system it introduced in 2019, which
# covers 2018 income, the survey leaves retirement account distributions to
# people under 58 out of total income.
CENSUS_COUNTED_IN_PART = {
    "retirement_distributions": "census_retirement_distributions",
}

# Sources CBO counts through the listed variable that sums them.
CBO_COUNTED_AS = {
    "medicaid": ("medicaid_cost",),
    "military_retirement_income": (
        "military_retirement_pay",
        "military_retirement_pay_survivors",
    ),
}

# Sources that can be losses.
LOSSES = {
    "self_employment_income",
    "sstb_self_employment_income",
    "partnership_s_corp_income",
    "farm_operations_income",
    "farm_rent_income",
    "rental_income",
    "estate_income",
}


CBO_LIST_NAMES = (
    "market_income_additions",
    "market_income_subtractions",
    "social_insurance_benefits",
    "means_tested_transfers",
    "federal_tax_subtractions",
)
BENEFIT_LIST_NAMES = (
    "household_benefits",
    "household_state_benefits",
    "household_local_benefits",
    "household_health_benefits",
    "household_head_start_benefits",
)


def dated_blocks(path):
    """A list parameter's (date, members) pairs, earliest first."""
    raw = yaml.load(path.read_text(), Loader=yaml.BaseLoader)
    return sorted(raw["values"].items())


def block(path, year):
    """The members of a list parameter in effect during a year.

    A year reads the block in effect on January 1, as the model does. The system
    backdates each list's first block to 2015, so a list applies before its
    first date too.
    """
    dated = dated_blocks(path)
    started = [members for date, members in dated if date <= f"{year}-01-01"]
    return set(started[-1] if started else dated[0][1])


def census_lists(year):
    return {
        source: block(CENSUS_LISTS / f"{source}.yaml", year)
        for source in CENSUS_SOURCES
    }


def census_members(year):
    return set().union(*census_lists(year).values())


def cbo_lists(year):
    return {
        name: block(HOUSEHOLD_LISTS / f"cbo_{name}.yaml", year)
        for name in CBO_LIST_NAMES
    }


def cbo_categories(year):
    """Each CBO total and the sources it counts; federal taxes subtract theirs."""
    lists = cbo_lists(year)
    market = block(MARKET_INCOME_SOURCES, year)
    return {
        "cbo_household_market_income": (market - lists["market_income_subtractions"])
        | lists["market_income_additions"],
        "cbo_household_social_insurance_benefits": lists["social_insurance_benefits"],
        "cbo_household_means_tested_transfers": lists["means_tested_transfers"],
        "cbo_household_federal_taxes": lists["federal_tax_subtractions"],
    }


def benefit_terms(year):
    """household_benefits with its state and local lists opened up.

    The health and Head Start totals stay whole: a switch turns each on.
    """
    terms = set()
    for name in block(HOUSEHOLD_LISTS / "household_benefits.yaml", year):
        if name in ("household_state_benefits", "household_local_benefits"):
            terms |= block(HOUSEHOLD_LISTS / f"{name}.yaml", year)
        else:
            terms.add(name)
    return terms


def benefit_leaves(year):
    """household_benefits with every nested list opened up."""
    leaves = set()
    for name in benefit_terms(year):
        if name in ("household_health_benefits", "household_head_start_benefits"):
            leaves |= block(HOUSEHOLD_LISTS / f"{name}.yaml", year)
        else:
            leaves.add(name)
    return leaves


def universe(year):
    """Every source that any concept's list counts during a year."""
    return (
        benefit_leaves(year)
        | block(MARKET_INCOME_SOURCES, year)
        | census_members(year)
        | set().union(*cbo_lists(year).values())
    )


def state_of(name):
    """The state that pays a program its name starts with, or Texas."""
    for match in re.finditer(r"(?:^|_)([a-z]{2})(?=_)", name):
        if match.group(1).upper() in STATES:
            return match.group(1).upper()
    return "TX"


@pytest.fixture(scope="module")
def variables():
    from policyengine_us.system import system

    return system.variables


@functools.cache
def entity_of(name):
    from policyengine_us.system import system

    return system.variables[name].entity.key


@functools.cache
def reachable(name, year):
    """A variable and every variable it reaches through `adds`."""
    from policyengine_us.system import system

    # `adds` can also name a parameter, which is a leaf.
    if name not in system.variables:
        return frozenset({name})
    parts = system.variables[name].adds or ()
    if isinstance(parts, str):
        node = functools.reduce(getattr, parts.split("."), system.parameters)
        parts = node(f"{year}-01-01")
    found = {name}
    for part in parts:
        found |= reachable(part, year)
    return frozenset(found)


def assert_none_sums_another(names, year):
    reached = {name: reachable(name, year) for name in names}
    for first, second in itertools.combinations(sorted(names), 2):
        both = reached[first] & reached[second]
        assert not both, f"{first} and {second} both count {sorted(both)}"


def test_census_lists_follow_appendix_a():
    files = {path.stem for path in CENSUS_LISTS.glob("*.yaml")} - {"index"}
    assert files == set(CENSUS_SOURCES)
    for number, source in enumerate(CENSUS_SOURCES, start=1):
        raw = yaml.load(
            (CENSUS_LISTS / f"{source}.yaml").read_text(), Loader=yaml.BaseLoader
        )
        assert f"source {number} of 18" in raw["description"], source
        titles = [reference["title"] for reference in raw["metadata"]["reference"]]
        assert any("P60-200, Appendix A" in title for title in titles), source
        # The definition applies to every year, so no year reads an empty list.
        assert min(raw["values"]) == "0000-01-01", source


def test_concept_lists_name_defined_variables(variables):
    names = set(CENSUS_EXCLUDED) | set(CBO_EXCLUDED)
    names |= set(CENSUS_COUNTED_AS) | set().union(*CENSUS_COUNTED_AS.values())
    names |= set(CENSUS_COUNTED_IN_PART) | set(CENSUS_COUNTED_IN_PART.values())
    names |= set(CBO_COUNTED_AS) | set().union(*CBO_COUNTED_AS.values())
    for year in YEARS:
        names |= census_members(year) | set().union(*cbo_lists(year).values())
    assert names - set(variables) == set()


def test_aliases_sum_exactly_their_parts(variables):
    # A part added to one of these variables later would otherwise reach
    # neither concept, or count where the concept leaves it out.
    for name, parts in {**CENSUS_COUNTED_AS, **CBO_COUNTED_AS}.items():
        assert set(variables[name].adds) == set(parts), name


def test_no_list_names_a_source_twice():
    # block() reads a list as a set, while a formula sums it as written.
    paths = [
        *(CENSUS_LISTS / f"{source}.yaml" for source in CENSUS_SOURCES),
        *(HOUSEHOLD_LISTS / f"cbo_{name}.yaml" for name in CBO_LIST_NAMES),
        *(HOUSEHOLD_LISTS / f"{name}.yaml" for name in BENEFIT_LIST_NAMES),
        MARKET_INCOME_SOURCES,
    ]
    repeats = [
        (path.stem, date, name)
        for path in paths
        for date, members in dated_blocks(path)
        for name, count in Counter(members).items()
        if count > 1
    ]
    assert repeats == []


@pytest.mark.parametrize("year", YEARS)
def test_no_source_counts_twice(year):
    seen = {}
    for source, members in census_lists(year).items():
        for name in members:
            assert name not in seen, f"{name} is under {seen[name]} and {source}"
            seen[name] = source
    assert_none_sums_another(set(seen), year)
    for name, partial in CENSUS_COUNTED_IN_PART.items():
        assert name not in seen, f"{name} counts beside {partial}, its counted part"
        assert partial in seen, f"{partial} no longer carries {name}"

    lists = cbo_lists(year)
    market = block(MARKET_INCOME_SOURCES, year)
    # An addition already in household market income would count twice, and a
    # subtraction missing from it would take away income never added.
    assert lists["market_income_additions"] & market == set()
    assert lists["market_income_subtractions"] <= market
    categories = cbo_categories(year)
    totals = list(categories)
    for index, first in enumerate(totals):
        for second in totals[index + 1 :]:
            both = categories[first] & categories[second]
            assert both == set(), f"{sorted(both)} count in {first} and {second}"
    assert_none_sums_another(set().union(*categories.values()), year)

    # household_market_income + household_benefits must not count a source
    # twice either, or the reconciliation below would not hold.
    assert market & benefit_terms(year) == set()


@pytest.mark.parametrize("year", YEARS)
def test_census_classifies_every_source(year):
    counted = census_members(year)
    counted |= {
        name for name, parts in CENSUS_COUNTED_AS.items() if set(parts) <= counted
    }
    counted |= {
        name for name, partial in CENSUS_COUNTED_IN_PART.items() if partial in counted
    }
    excluded = set(CENSUS_EXCLUDED)
    assert counted & excluded == set(), "listed and excluded"
    unclassified = universe(year) - counted - excluded
    assert unclassified == set(), (
        f"{year}: {sorted(unclassified)} reach another income concept but "
        "neither a Census money income list nor CENSUS_EXCLUDED. Add each to "
        "the Appendix A source that covers it, or document why money income "
        "leaves it out."
    )


@pytest.mark.parametrize("year", YEARS)
def test_cbo_classifies_every_source(year):
    counted = set().union(*cbo_categories(year).values())
    for alias, parts in CBO_COUNTED_AS.items():
        if alias in counted:
            counted |= set(parts)
    excluded = set(CBO_EXCLUDED)
    assert counted & excluded == set(), "listed and excluded"
    unclassified = universe(year) - counted - excluded
    assert unclassified == set(), (
        f"{year}: {sorted(unclassified)} reach another income concept but no "
        "CBO category and not CBO_EXCLUDED. Add each to the CBO list that "
        "covers it, or document why CBO leaves it out."
    )
    # Each source CBO removes from household market income says why.
    assert cbo_lists(year)["market_income_subtractions"] <= excluded


def test_exclusions_are_current():
    every_year = set().union(*(universe(year) for year in YEARS))
    assert set(CENSUS_EXCLUDED) - every_year == set(), "stale Census entries"
    assert set(CENSUS_COUNTED_AS) - every_year == set(), "stale Census aliases"
    assert set(CENSUS_COUNTED_IN_PART) - every_year == set(), "stale Census parts"
    assert set(CBO_EXCLUDED) - every_year == set(), "stale CBO entries"
    aliased = set(CBO_COUNTED_AS) | set().union(*CBO_COUNTED_AS.values())
    assert aliased - every_year == set(), "stale CBO aliases"


def paired_households(cases, size, year, earnings=0, ages=None):
    """A paid and an unpaid household for each (name, entity, state, amount).

    Each household holds a head, 40 years old unless `ages` gives one per case,
    who earns `earnings`, and `size - 1` children, in one tax unit, SPM unit and
    family. A source the situation names becomes an input for every household,
    zero where unset, so no formula responds to another case's payment.
    """
    people = {}
    units = {
        "tax_units": {},
        "spm_units": {},
        "families": {},
        "marital_units": {},
        "households": {},
    }
    for index, (name, entity, state, amount) in enumerate(cases):
        for side, value in (("paid", amount), ("zero", 0)):
            key = f"{side}_{index}"
            members = [f"{key}_{position}" for position in range(size)]
            for position, member in enumerate(members):
                head_age = 40 if ages is None else ages[index]
                people[member] = {"age": {year: head_age if position == 0 else 10}}
                units["marital_units"][member] = {"members": [member]}
            head = people[members[0]]
            head["employment_income"] = {year: earnings}
            groups = {
                "person": head,
                "marital_unit": units["marital_units"][members[0]],
                "tax_unit": {"members": members},
                "spm_unit": {"members": members},
                "family": {"members": members},
                "household": {"members": members, "state_name": {year: state}},
            }
            if name == "employment_income":
                value += earnings
            groups[entity][name] = {year: value}
            units["tax_units"][key] = groups["tax_unit"]
            units["spm_units"][key] = groups["spm_unit"]
            units["families"][key] = groups["family"]
            units["households"][key] = groups["household"]
    return Simulation(situation={"people": people, **units})


def values_by_id(simulation, variable, year):
    entity = simulation.tax_benefit_system.variables[variable].entity.key
    ids = simulation.populations[entity].ids
    return dict(zip(ids, simulation.calculate(variable, year).astype(float)))


def change(values, index, member=None):
    suffix = "" if member is None else f"_{member}"
    return values[f"paid_{index}{suffix}"] - values[f"zero_{index}{suffix}"]


def shares(entity, amount, size):
    """What each member gains: a person's own source, or an equal share."""
    if entity in ("person", "marital_unit"):
        return [amount] + [0] * (size - 1)
    return [amount / size] * size


def census_cases(year):
    return sorted(census_members(year) | (set(CENSUS_EXCLUDED) & universe(year)))


CENSUS_CASE_COUNT = max(len(census_cases(year)) for year in YEARS)


@pytest.mark.parametrize("year", YEARS)
@settings(max_examples=2, deadline=None)
@given(
    size=st.integers(min_value=1, max_value=3),
    amounts=st.lists(
        st.integers(min_value=1, max_value=100_000),
        min_size=CENSUS_CASE_COUNT,
        max_size=CENSUS_CASE_COUNT,
    ),
    losses=st.booleans(),
)
@example(
    size=3,
    amounts=[1_000 + index for index in range(CENSUS_CASE_COUNT)],
    losses=True,
)
def test_census_money_income_moves_dollar_for_dollar(year, size, amounts, losses):
    counted = census_members(year)
    cases = []
    for name, amount in zip(census_cases(year), amounts):
        if losses and name in LOSSES:
            amount = -amount
        cases.append((name, entity_of(name), state_of(name), amount))
    simulation = paired_households(cases, size, year)
    person = values_by_id(simulation, "census_money_income", year)
    family = values_by_id(simulation, "census_family_money_income", year)
    household = values_by_id(simulation, "census_household_money_income", year)

    failures = []
    for index, (name, entity, _, amount) in enumerate(cases):
        expected = amount if name in counted else 0
        observed = [change(person, index, member) for member in range(size)]
        if not np.allclose(observed, shares(entity, expected, size), atol=TOLERANCE):
            failures.append((name, "person", observed, expected))
        for label, values in (("family", family), ("household", household)):
            if abs(change(values, index) - expected) > TOLERANCE:
                failures.append((name, label, change(values, index), expected))
    assert failures == []


@pytest.mark.parametrize("year", (2017, 2018, 2026))
@settings(max_examples=3, deadline=None)
@given(amount=st.integers(min_value=1, max_value=200_000))
@example(amount=10_000)
def test_census_counts_retirement_distributions_from_age_58(year, amount):
    # The redesigned processing system the survey introduced in 2019, which
    # covers 2018 income, leaves distributions to people under 58 out of total
    # income; Appendix A has no age limit.
    ages = list(range(15, 91))
    cases = [("retirement_distributions", "person", "TX", amount)] * len(ages)
    # Earnings this high rule out every means-tested response.
    simulation = paired_households(cases, 1, year, earnings=100_000, ages=ages)
    person = values_by_id(simulation, "census_money_income", year)
    household = values_by_id(simulation, "census_household_money_income", year)
    for index, age in enumerate(ages):
        expected = amount if year < 2018 or age >= 58 else 0
        assert change(person, index, 0) == pytest.approx(expected, abs=TOLERANCE), age
        assert change(household, index) == pytest.approx(expected, abs=TOLERANCE), age


def cbo_cases(year):
    return sorted(
        set().union(*cbo_categories(year).values())
        | (set(CBO_EXCLUDED) & universe(year))
    )


CBO_CASE_COUNT = max(len(cbo_cases(year)) for year in YEARS)


@pytest.mark.parametrize("year", YEARS)
@settings(max_examples=2, deadline=None)
@given(
    size=st.integers(min_value=1, max_value=3),
    amounts=st.lists(
        st.integers(min_value=1, max_value=100_000),
        min_size=CBO_CASE_COUNT,
        max_size=CBO_CASE_COUNT,
    ),
)
@example(size=2, amounts=[1_000 + index for index in range(CBO_CASE_COUNT)])
def test_cbo_categories_move_dollar_for_dollar(year, size, amounts):
    categories = cbo_categories(year)
    subtractions = cbo_lists(year)["market_income_subtractions"]
    cases = [
        (name, entity_of(name), state_of(name), amount)
        for name, amount in zip(cbo_cases(year), amounts)
    ]
    simulation = paired_households(cases, size, year)
    # Federal taxes respond to income, so the next test checks them alone.
    incomes = {key: value for key, value in categories.items() if key in CBO_INCOMES}
    totals = {total: values_by_id(simulation, total, year) for total in incomes}
    market = values_by_id(simulation, "household_market_income", year)

    failures = []
    for index, (name, _, _, amount) in enumerate(cases):
        for total, members in incomes.items():
            expected = amount if name in members else 0
            if abs(change(totals[total], index) - expected) > TOLERANCE:
                failures.append((name, total, change(totals[total], index), expected))
        if name in subtractions and abs(change(market, index) - amount) > TOLERANCE:
            failures.append((name, "household_market_income", change(market, index)))
    assert failures == []


@pytest.mark.parametrize("year", YEARS)
@settings(max_examples=2, deadline=None)
@given(amount=st.integers(min_value=1, max_value=20_000))
@example(amount=4_321)
def test_cbo_federal_taxes_subtract_each_refundable_credit(year, amount):
    credits = sorted(cbo_categories(year)["cbo_household_federal_taxes"])
    cases = [(name, entity_of(name), "TX", amount) for name in credits]
    # Earnings this high rule out every means-tested response.
    simulation = paired_households(cases, 2, year, earnings=500_000)
    taxes = values_by_id(simulation, "cbo_household_federal_taxes", year)
    for index, name in enumerate(credits):
        assert change(taxes, index) == pytest.approx(-amount, abs=TOLERANCE), name


@pytest.mark.parametrize(
    "year, name, alias",
    [
        (year, name, alias)
        for year in YEARS
        for alias, parts in CBO_COUNTED_AS.items()
        for name in parts
    ],
)
def test_cbo_counts_a_source_through_the_variable_that_sums_it(year, name, alias):
    simulation = paired_households(
        [(name, entity_of(name), "TX", 1_000)], 1, year, earnings=500_000
    )
    categories = cbo_categories(year)
    assert any(alias in categories[total] for total in CBO_INCOMES), alias
    for total in CBO_INCOMES:
        expected = 1_000 if alias in categories[total] else 0
        assert change(values_by_id(simulation, total, year), 0) == pytest.approx(
            expected, abs=TOLERANCE
        ), total


def reference_census_money_income(simulation, year):
    """census_money_income rebuilt from its sources with numpy.

    A person keeps their own sources and an equal share of each group's.
    """
    total = np.zeros(simulation.persons.count)
    for name in census_members(year):
        entity = simulation.tax_benefit_system.variables[name].entity
        values = simulation.calculate(name, year).astype(float)
        if entity.is_person:
            total += values
        else:
            population = simulation.populations[entity.key]
            group = population.members_entity_id
            size = np.bincount(group, minlength=population.count)
            total += values[group] / size[group]
    return total


def members_by_group(names, assignment):
    """Each group's members, keyed by the group number the assignment gives."""
    groups = {}
    for name, group in zip(names, assignment):
        groups.setdefault(group, []).append(name)
    return groups


@pytest.mark.parametrize("year", YEARS)
@settings(max_examples=2, deadline=None)
@given(
    spm_unit_of=st.lists(st.integers(min_value=0, max_value=2), min_size=1, max_size=5),
    tax_unit_of=st.lists(st.integers(min_value=0, max_value=2), min_size=5, max_size=5),
    family_of=st.lists(st.integers(min_value=0, max_value=2), min_size=5, max_size=5),
    earnings=st.lists(
        st.integers(min_value=0, max_value=60_000), min_size=5, max_size=5
    ),
    veterans=st.lists(
        st.integers(min_value=0, max_value=20_000), min_size=5, max_size=5
    ),
    tanf=st.lists(st.integers(min_value=0, max_value=10_000), min_size=3, max_size=3),
    basic_income=st.lists(
        st.integers(min_value=0, max_value=10_000), min_size=3, max_size=3
    ),
    infant_supplement=st.integers(min_value=0, max_value=10_000),
    state=st.sampled_from(STATES),
)
@example(
    spm_unit_of=[0, 0, 1, 1, 1],
    tax_unit_of=[0, 1, 2, 2, 2],
    family_of=[0, 0, 1, 1, 1],
    earnings=[20_000, 0, 9_000, 0, 0],
    veterans=[0, 0, 3_000, 0, 0],
    tanf=[1_000, 900, 0],
    basic_income=[100, 200, 300],
    infant_supplement=1_000,
    state="CA",
)
def test_totals_sum_members_and_match_an_independent_allocation(
    year,
    spm_unit_of,
    tax_unit_of,
    family_of,
    earnings,
    veterans,
    tanf,
    basic_income,
    infant_supplement,
    state,
):
    # One household holds up to three SPM units, tax units and families, drawn
    # separately, so a split by the wrong group fails.
    names = [f"person_{index}" for index in range(len(spm_unit_of))]
    people = {
        name: {
            "age": {year: 25 + 10 * index},
            "employment_income": {year: earnings[index]},
            "veterans_benefits": {year: veterans[index]},
        }
        for index, name in enumerate(names)
    }
    simulation = Simulation(
        situation={
            "people": people,
            "tax_units": {
                f"tax_unit_{group}": {
                    "members": members,
                    "basic_income": {year: basic_income[group]},
                }
                for group, members in members_by_group(names, tax_unit_of).items()
            },
            "spm_units": {
                f"spm_unit_{group}": {
                    "members": members,
                    "tanf": {year: tanf[group]},
                }
                for group, members in members_by_group(names, spm_unit_of).items()
            },
            "families": {
                f"family_{group}": {"members": members}
                for group, members in members_by_group(names, family_of).items()
            },
            "marital_units": {name: {"members": [name]} for name in names},
            "households": {
                "household": {
                    "members": names,
                    "state_name": {year: state},
                    "ca_la_infant_supplement": {year: infant_supplement},
                }
            },
        }
    )
    person = simulation.calculate("census_money_income", year).astype(float)
    family = simulation.calculate("census_family_money_income", year).astype(float)
    household = simulation.calculate("census_household_money_income", year)
    assert household.sum() == pytest.approx(person.sum(), abs=TOLERANCE)
    members_family = simulation.populations["family"].members_entity_id
    assert np.allclose(
        family,
        np.bincount(members_family, weights=person, minlength=family.size),
        atol=TOLERANCE,
    )
    assert np.allclose(
        person, reference_census_money_income(simulation, year), atol=TOLERANCE
    )


@pytest.mark.parametrize("year", YEARS)
@settings(max_examples=1, deadline=None)
@given(
    earnings=st.lists(
        st.integers(min_value=0, max_value=150_000),
        min_size=len(STATES),
        max_size=len(STATES),
    ),
    children=st.integers(min_value=0, max_value=2),
)
@example(earnings=[15_000] * len(STATES), children=2)
def test_census_money_income_reconciles_with_household_totals(year, earnings, children):
    """A differential test of Census money income in every state at once.

    household_market_income and household_benefits sum their own lists. Take
    away the terms money income leaves out and add the sources only money
    income counts, and the result is Census household money income. The test
    reads the same lists as the variables, so it checks how the variables add
    them, not where a program belongs.

    Each state has a working-age household with children, an aged person and a
    disabled person, with rent, so that state cash and rent-tested programs pay.
    """
    people, units = {}, {key: {} for key in ("tax_units", "spm_units", "families")}
    marital_units, households = {}, {}

    def add_household(key, state, ages, income, **head_inputs):
        members = [f"{key}_{index}" for index in range(len(ages))]
        for member, age in zip(members, ages):
            people[member] = {"age": {year: age}}
            marital_units[member] = {"members": [member]}
        people[members[0]].update(
            employment_income={year: income},
            pre_subsidy_rent={year: 12_000},
            **{name: {year: value} for name, value in head_inputs.items()},
        )
        for unit in units.values():
            unit[key] = {"members": members}
        households[key] = {"members": members, "state_name": {year: state}}

    for state, amount in zip(STATES, earnings):
        add_household(
            f"{state}_working",
            state,
            [40] + [6 + child for child in range(children)],
            amount,
        )
        add_household(f"{state}_aged", state, [70], 0)
        add_household(f"{state}_disabled", state, [45], 0, is_disabled=True)
    simulation = Simulation(
        situation={
            "people": people,
            **units,
            "marital_units": marital_units,
            "households": households,
        }
    )

    def household_total(name):
        return simulation.calculate(name, year, map_to="household").astype(float)

    terms = block(MARKET_INCOME_SOURCES, year) | benefit_terms(year)
    census = census_members(year)
    reconciled = household_total("household_market_income") + household_total(
        "household_benefits"
    )
    for name in terms - census:
        reconciled -= household_total(name)
    for name in census - terms:
        reconciled += household_total(name)
    assert np.allclose(
        household_total("census_household_money_income"),
        reconciled,
        atol=RECONCILIATION_TOLERANCE,
    )
