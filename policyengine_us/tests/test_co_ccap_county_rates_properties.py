"""Colorado's Child Care Assistance Program pays no more than the county rate.

8 CCR 1403-1 3.125(FFF) pays the lesser of the provider's charge and the
county reimbursement rate. 3.130 sets that rate: a full-time daily rate by
county, provider type, age band and, for licensed providers, quality level,
paid in care units: part time through 5 hours a day at 55% of the full-time
rate, full time through 12 hours, full time plus part time through 17, and two
full-time units through 24. 3.124(K) and (L) take the parent fee from the
first dollars and never let it exceed the reimbursement.

These tests read the rate tables straight from the parameter files and
recompute each rate by the rule, apart from the model's formulas:

1. The model's full-time daily rate equals the table's cell for the child's
   county (Denver's for a county outside Colorado's list), provider type, age
   band and quality tier, on the date in force. One test checks every cell on
   every date a table or county plan changed a rate.
2. Each care unit pays the full-time rate times the unit, rounded half up to
   the cent, as the county rate plans print it: a part-time day pays 55% of a
   full-time day, and two full-time units pay twice a full-time day.
3. Each eligible child's reimbursement is the lesser of the child's charges
   and the daily rate times the days of care, and the payment is the sum less
   the parent fee, never below zero. So the payment never exceeds the county
   rate for the care, nor the charges less the fee; the capped fee never
   exceeds the fee or the reimbursement; and the payment plus the capped fee
   equals the reimbursement.
4. More charges never lower the payment, and a higher fee never raises it.

Without daily hours, the model spreads a child's weekly hours over the days
of care in a week: the larger of days a week and attending days a month x
12 / 52, else five weekdays. Without hours of care a child takes the full-time
unit, and without a weekly schedule or attending days, a five-day week
(5 x 52 / 12 days a month).
"""

from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import pytest
import yaml
from hypothesis import example, given, settings
from hypothesis import strategies as st

import policyengine_us
from policyengine_us import Simulation

RATES = Path(policyengine_us.__file__).parent / ("parameters/gov/states/co/ccap/rates")
TOLERANCE = 0.01
CENT = Decimal("0.01")
WEEKS_IN_YEAR = 52
MONTHS_IN_YEAR = 12
DEFAULT_DAYS_PER_WEEK = 5
PARENT_AGE = 30
# A county outside Colorado's list reads Denver's rates.
FALLBACK_COUNTY = "DENVER_COUNTY_CO"
# The bands as CDEC's tables head them, in months of age.
CENTER_BANDS = (
    (18, "MONTHS_0_TO_18"),
    (36, "MONTHS_18_TO_36"),
    (72, "MONTHS_36_TO_YEARS_6"),
)
HOME_BANDS = ((24, "MONTHS_0_TO_24"), (72, "MONTHS_24_TO_YEARS_6"))
EXEMPT_BANDS = ((60, "UNDER_5"),)
SCHOOL_AGE = "SCHOOL_AGE"
EXEMPT_OLDER = "AGE_5_AND_OVER"
CENTER = "DCC_SACC"
HOME = "FDC_GFDC"
PROVIDER_GROUPS = [CENTER, HOME, "LE_GC", "LE_STD", "LE_ENH"]
# One age and one rating that land in each band and tier.
CENTER_AGES = {
    "MONTHS_0_TO_18": 12,
    "MONTHS_18_TO_36": 24,
    "MONTHS_36_TO_YEARS_6": 48,
    SCHOOL_AGE: 96,
}
HOME_AGES = {"MONTHS_0_TO_24": 12, "MONTHS_24_TO_YEARS_6": 48, SCHOOL_AGE: 96}
EXEMPT_AGES = {"UNDER_5": 12, EXEMPT_OLDER: 96}
TIER_RATINGS = {"TIER_1_2": 0, "TIER_3": 3, "TIER_4_5": 5}


def table(name):
    tree = yaml.safe_load((RATES / f"{name}.yaml").read_text())
    return {key: value for key, value in tree.items() if key.endswith("_CO")}


CENTER_RATES = table("licensed_center")
HOME_RATES = table("licensed_home")
EXEMPT_RATES = table("qualified_exempt")
COUNTIES = sorted(EXEMPT_RATES)


def effective_dates(node):
    if isinstance(node, dict):
        dates = set()
        for key, value in node.items():
            dates |= {key} if isinstance(key, date) else effective_dates(value)
        return dates
    return set()


EFFECTIVE_DATES = sorted(
    effective_dates(CENTER_RATES)
    | effective_dates(HOME_RATES)
    | effective_dates(EXEMPT_RATES)
)


def in_force(values, instant):
    """The value on `instant`. Before the first date, the first value, which
    CountryTaxBenefitSystem backdates."""
    starts = sorted(values)
    value = values[starts[0]]
    for start in starts:
        if start <= instant:
            value = values[start]
    return Decimal(str(value))


def band(age_months, bands, oldest):
    for limit, name in bands:
        if age_months < limit:
            return name
    return oldest


def tier(rating):
    if rating >= 4:
        return "TIER_4_5"
    if rating == 3:
        return "TIER_3"
    return "TIER_1_2"


def full_time_rate(county, provider, age_months, rating, instant):
    """3.130: the table cell for the child's care."""
    county = county if county in EXEMPT_RATES else FALLBACK_COUNTY
    if provider == CENTER:
        cell = CENTER_RATES[county][band(age_months, CENTER_BANDS, SCHOOL_AGE)]
        return in_force(cell[tier(rating)], instant)
    if provider == HOME:
        cell = HOME_RATES[county][band(age_months, HOME_BANDS, SCHOOL_AGE)]
        return in_force(cell[tier(rating)], instant)
    # Colorado pays license-exempt care through qualified exempt providers.
    cell = EXEMPT_RATES[county][band(age_months, EXEMPT_BANDS, EXEMPT_OLDER)]
    return in_force(cell, instant)


def care_hours(child):
    """The child's daily hours, else weekly hours over the days of care."""
    if child["hours"] > 0:
        return child["hours"]
    reported_days = max(
        child["days_per_week"],
        child["attending_days"] * MONTHS_IN_YEAR / WEEKS_IN_YEAR,
    )
    days_in_a_week = reported_days if reported_days > 0 else DEFAULT_DAYS_PER_WEEK
    return child["weekly_hours"] / days_in_a_week


def care_unit(hours):
    """3.130(C); without hours, the full-time unit."""
    if hours <= 0:
        return Decimal("1")
    if hours <= 5:
        return Decimal("0.55")
    if hours <= 12:
        return Decimal("1")
    if hours <= 17:
        return Decimal("1.55")
    return Decimal("2")


def daily_rate(full_time, unit):
    return (full_time * unit).quantize(CENT, rounding=ROUND_HALF_UP)


def days_of_care(days_per_week, attending_days):
    days = max(days_per_week * WEEKS_IN_YEAR / MONTHS_IN_YEAR, attending_days)
    if days > 0:
        return days
    return DEFAULT_DAYS_PER_WEEK * WEEKS_IN_YEAR / MONTHS_IN_YEAR


def county_rate(child, county, instant):
    """The most the county pays for the child's care in the month."""
    full_time = full_time_rate(
        county, child["provider"], child["age_months"], child["rating"], instant
    )
    daily = daily_rate(full_time, care_unit(care_hours(child)))
    return float(daily) * days_of_care(child["days_per_week"], child["attending_days"])


def simulate(month, units, variables):
    """`variables` for `month`, with each unit one Colorado household, SPM
    unit and tax unit of a parent and the unit's children.

    Returns each variable's values by person, or by SPM unit for SPM unit
    variables, in the order of `units` and their children."""
    year = int(month[:4])
    people, households, spm_units, tax_units, families, marital_units = (
        {},
        {},
        {},
        {},
        {},
        {},
    )
    for u, unit in enumerate(units):
        parent = f"parent_{u}"
        people[parent] = {"age": {year: PARENT_AGE}}
        marital_units[f"marital_unit_{parent}"] = {"members": [parent]}
        members = [parent]
        for c, child in enumerate(unit["children"]):
            name = f"child_{u}_{c}"
            members.append(name)
            marital_units[f"marital_unit_{name}"] = {"members": [name]}
            people[name] = {
                "age": {year: child["age_months"] / MONTHS_IN_YEAR},
                "is_tax_unit_dependent": {year: True},
                "childcare_provider_type_group": {year: child["provider"]},
                "co_quality_rating_of_child_care_facility": {year: child["rating"]},
                "childcare_hours_per_day": {year: child["hours"]},
                "childcare_hours_per_week": {year: child["weekly_hours"]},
                "childcare_days_per_week": {year: child["days_per_week"]},
                "childcare_attending_days_per_month": {year: child["attending_days"]},
                "pre_subsidy_childcare_expenses": {
                    year: child["charge"] * MONTHS_IN_YEAR
                },
            }
        households[f"household_{u}"] = {
            "members": members,
            "state_code": {year: "CO"},
            "county": {year: unit["county"]},
        }
        spm_units[f"spm_unit_{u}"] = {
            "members": members,
            "co_ccap_eligible": {month: True},
            "co_ccap_parent_fee": {month: unit["fee"]},
        }
        tax_units[f"tax_unit_{u}"] = {"members": members}
        families[f"family_{u}"] = {"members": members}
    simulation = Simulation(
        situation={
            "people": people,
            "households": households,
            "spm_units": spm_units,
            "tax_units": tax_units,
            "families": families,
            "marital_units": marital_units,
        }
    )
    results = {}
    for variable in variables:
        values = simulation.calculate(variable, month)
        if simulation.tax_benefit_system.variables[variable].entity.key == "person":
            # Drop the parents, leaving the children in order.
            children = [i for i, name in enumerate(people) if name.startswith("child_")]
            values = values[children]
        results[variable] = [float(value) for value in values]
    return results


def instant_of(month):
    year, month_number = month.split("-")
    return date(int(year), int(month_number), 1)


months = st.builds(
    lambda year, month: f"{year}-{month:02d}",
    st.integers(min_value=2023, max_value=2027),
    st.integers(min_value=1, max_value=12),
)
hours = st.one_of(
    st.integers(min_value=0, max_value=24),
    st.sampled_from([5, 5.5, 12, 12.5, 17, 17.5]),
)
# Whole hours a week, with the amounts that land on 5, 12 and 17 hours a day
# over five weekdays.
weekly_hours = st.one_of(
    st.integers(min_value=0, max_value=120),
    st.sampled_from([25, 26, 60, 61, 85, 86]),
)
children = st.fixed_dictionaries(
    dict(
        # Children under 13, whose care 3.132(D) covers.
        age_months=st.integers(min_value=0, max_value=155),
        provider=st.sampled_from(PROVIDER_GROUPS),
        rating=st.integers(min_value=0, max_value=5),
        hours=hours,
        weekly_hours=weekly_hours,
        days_per_week=st.integers(min_value=0, max_value=7),
        attending_days=st.integers(min_value=0, max_value=31),
        charge=st.integers(min_value=0, max_value=4_000),
    )
)
units = st.fixed_dictionaries(
    dict(
        county=st.sampled_from([*COUNTIES, "UNKNOWN"]),
        fee=st.integers(min_value=0, max_value=2_000),
        children=st.lists(children, min_size=1, max_size=3),
    )
)


def child(**overrides):
    base = dict(
        age_months=0,
        provider=CENTER,
        rating=0,
        hours=0,
        weekly_hours=0,
        days_per_week=0,
        attending_days=0,
        charge=0,
    )
    return {**base, **overrides}


@pytest.mark.parametrize("effective", EFFECTIVE_DATES, ids=str)
def test_every_cell_matches_its_table(effective):
    month = f"{effective.year}-{effective.month:02d}"
    county_cells = [
        *[
            (CENTER, age, rating)
            for age in CENTER_AGES.values()
            for rating in TIER_RATINGS.values()
        ],
        *[
            (HOME, age, rating)
            for age in HOME_AGES.values()
            for rating in TIER_RATINGS.values()
        ],
        *[("LE_STD", age, 0) for age in EXEMPT_AGES.values()],
    ]
    cells = [(county, *cell) for county in COUNTIES for cell in county_cells]
    units = [
        dict(
            county=county,
            fee=0,
            children=[
                child(age_months=age, provider=provider, rating=rating)
                for provider, age, rating in county_cells
            ],
        )
        for county in COUNTIES
    ]
    rates = simulate(month, units, ["co_ccap_full_time_daily_rate"])
    model = rates["co_ccap_full_time_daily_rate"]
    expected = [
        float(full_time_rate(county, provider, age, rating, effective))
        for county, provider, age, rating in cells
    ]
    assert len(model) == len(expected)
    mismatches = [
        (cell, got, want)
        for cell, got, want in zip(cells, model, expected)
        if abs(got - want) > TOLERANCE / 10
    ]
    assert not mismatches, mismatches[:5]


@settings(max_examples=15, deadline=None)
# Adams County's infant rate in January 2025: $73.90 a day, $40.65 part time.
@example(
    month="2025-01", unit=dict(county="ADAMS_COUNTY_CO", fee=0, children=[child()])
)
# Weld County's qualified exempt plan of February 1, 2025.
@example(
    month="2025-02",
    unit=dict(
        county="WELD_COUNTY_CO",
        fee=0,
        children=[child(age_months=48, provider="LE_GC")],
    ),
)
# A county outside Colorado's list, at the age band boundaries.
@example(
    month="2026-06",
    unit=dict(
        county="UNKNOWN",
        fee=0,
        children=[
            child(age_months=18, provider=CENTER, rating=3),
            child(age_months=24, provider=HOME, rating=4),
            child(age_months=60, provider="LE_ENH"),
        ],
    ),
)
@given(month=months, unit=units)
def test_each_care_unit_pays_its_share_of_the_full_time_rate(month, unit):
    instant = instant_of(month)
    # Price each child's care at each unit: 4, 8, 14 and 20 hours a day.
    unit_hours = [4, 8, 14, 20]
    copies = dict(
        county=unit["county"],
        fee=0,
        children=[
            {**kid, "hours": hours_a_day}
            for kid in unit["children"]
            for hours_a_day in unit_hours
        ],
    )
    rates = simulate(
        month, [copies], ["co_ccap_full_time_daily_rate", "co_ccap_daily_rate"]
    )
    full_time = rates["co_ccap_full_time_daily_rate"]
    daily = rates["co_ccap_daily_rate"]
    for k, kid in enumerate(unit["children"]):
        expected = full_time_rate(
            unit["county"], kid["provider"], kid["age_months"], kid["rating"], instant
        )
        part, full, full_and_part, two_full = daily[4 * k : 4 * k + 4]
        assert full_time[4 * k] == pytest.approx(float(expected), abs=TOLERANCE / 10)
        assert full == pytest.approx(float(expected), abs=TOLERANCE / 10)
        assert part == pytest.approx(
            float(daily_rate(expected, Decimal("0.55"))), abs=TOLERANCE / 10
        )
        assert full_and_part == pytest.approx(
            float(daily_rate(expected, Decimal("1.55"))), abs=TOLERANCE / 10
        )
        assert two_full == pytest.approx(float(2 * expected), abs=TOLERANCE / 10)


@settings(max_examples=20, deadline=None)
# An infant's $2,000 in an Adams County center against $1,662.05, less $100.
@example(
    month="2026-01",
    many=[dict(county="ADAMS_COUNTY_CO", fee=100, children=[child(charge=2_000)])],
)
# A fee above the reimbursement.
@example(
    month="2026-01",
    many=[dict(county="ADAMS_COUNTY_CO", fee=2_000, children=[child(charge=2_000)])],
)
# Weekly hours alone, at each edge of a care unit over five weekdays.
@example(
    month="2026-01",
    many=[
        dict(
            county="ADAMS_COUNTY_CO",
            fee=0,
            children=[
                child(weekly_hours=25, charge=4_000),
                child(weekly_hours=26, charge=4_000),
                child(weekly_hours=60, charge=4_000),
                child(weekly_hours=61, charge=4_000),
                child(weekly_hours=85, charge=4_000),
                child(weekly_hours=86, charge=4_000),
            ],
        )
    ],
)
# Two children, one capped and one below the cap, with schedules.
@example(
    month="2025-03",
    many=[
        dict(
            county="BOULDER_COUNTY_CO",
            fee=50,
            children=[
                child(age_months=96, hours=4, days_per_week=3, charge=400),
                child(
                    age_months=30,
                    provider=HOME,
                    rating=5,
                    hours=13,
                    attending_days=25,
                    days_per_week=5,
                    charge=4_000,
                ),
            ],
        )
    ],
)
@given(month=months, many=st.lists(units, min_size=1, max_size=4))
def test_the_payment_is_the_capped_charges_less_the_fee(month, many):
    instant = instant_of(month)
    results = simulate(
        month,
        many,
        [
            "co_ccap_maximum_monthly_payment",
            "co_ccap_reimbursement",
            "co_ccap_capped_parent_fee",
            "co_ccap_subsidy",
        ],
    )
    caps = iter(results["co_ccap_maximum_monthly_payment"])
    for u, unit in enumerate(many):
        rates = [county_rate(kid, unit["county"], instant) for kid in unit["children"]]
        for rate in rates:
            assert next(caps) == pytest.approx(rate, abs=TOLERANCE)
        charges = [kid["charge"] for kid in unit["children"]]
        reimbursement = sum(min(c, r) for c, r in zip(charges, rates))
        fee = unit["fee"]
        model_reimbursement = results["co_ccap_reimbursement"][u]
        capped_fee = results["co_ccap_capped_parent_fee"][u]
        paid = results["co_ccap_subsidy"][u]
        assert model_reimbursement == pytest.approx(reimbursement, abs=TOLERANCE)
        assert capped_fee == pytest.approx(min(fee, reimbursement), abs=TOLERANCE)
        assert paid == pytest.approx(max(reimbursement - fee, 0), abs=TOLERANCE)
        # The bounds and the identity the rule implies.
        assert -TOLERANCE <= paid <= sum(rates) + TOLERANCE
        assert paid <= max(sum(charges) - fee, 0) + TOLERANCE
        assert capped_fee <= min(fee, model_reimbursement) + TOLERANCE
        assert paid + capped_fee == pytest.approx(model_reimbursement, abs=TOLERANCE)


@settings(max_examples=15, deadline=None)
@example(
    month="2026-01",
    unit=dict(county="ADAMS_COUNTY_CO", fee=100, children=[child(charge=1_600)]),
    more_charge=200,
    more_fee=50,
)
@given(
    month=months,
    unit=units,
    more_charge=st.integers(min_value=1, max_value=2_000),
    more_fee=st.integers(min_value=1, max_value=1_000),
)
def test_more_charges_never_lower_the_payment_and_a_higher_fee_never_raises_it(
    month, unit, more_charge, more_fee
):
    first, *others = unit["children"]
    costlier = dict(
        unit, children=[{**first, "charge": first["charge"] + more_charge}, *others]
    )
    pricier_fee = dict(unit, fee=unit["fee"] + more_fee)
    paid = simulate(month, [unit, costlier, pricier_fee], ["co_ccap_subsidy"])[
        "co_ccap_subsidy"
    ]
    base, with_more_charge, with_more_fee = paid
    assert with_more_charge >= base - TOLERANCE
    assert with_more_fee <= base + TOLERANCE
