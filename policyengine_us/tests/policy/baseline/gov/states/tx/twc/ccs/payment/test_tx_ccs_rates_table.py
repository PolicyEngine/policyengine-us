"""The Texas CCS four-age-group rate table obeys the rules that set it.

The table holds seven statewide TWC tables, from WD Letter 12-18 (effective
August 1, 2018) to BCY 2025. 40 TAC §809.20(c)-(d) sets Texas Rising Star
rates at least 5, 7 and 9 percent above a provider's regular rate, and a
Texas School Ready (TSR) rate at least 5 percent above it for the age groups
in §809.20(b)(2). Each rate letter from WD 12-18 to WD 20-23 says no provider
rate will be reduced, and WD Letter 19-24, Change 1, keeps every BCY 2025
rate at or above its BCY 2024 level, except relative care, which Boards set
locally. Each check runs over all 4,032 cells of every table, so a value
copied into the wrong cell fails here. The test reads the YAML file directly
and builds no tax-benefit system.
"""

import datetime
from decimal import ROUND_HALF_UP, Decimal
from functools import reduce
from pathlib import Path

import pytest
import yaml
from hypothesis import given, settings
from hypothesis import strategies as st
from policyengine_core.parameters import load_parameter_file

PACKAGE = next(
    parent
    for parent in Path(__file__).resolve().parents
    if parent.name == "policyengine_us"
)
RATES = PACKAGE / "parameters/gov/states/tx/twc/ccs/payment/rates.yaml"

WD_12_18 = datetime.date(2018, 8, 1)
BCY_2020 = datetime.date(2019, 10, 1)
BCY_2021 = datetime.date(2020, 10, 1)
BCY_2022 = datetime.date(2021, 10, 1)
BCY_2023 = datetime.date(2022, 10, 1)
BCY_2024 = datetime.date(2023, 10, 1)
BCY_2025 = datetime.date(2024, 10, 1)
YEARS = [WD_12_18, BCY_2020, BCY_2021, BCY_2022, BCY_2023, BCY_2024, BCY_2025]

TRS_MARKUP = {
    "TRS2": Decimal("1.05"),
    "TRS3": Decimal("1.07"),
    "TRS4": Decimal("1.09"),
}
TSR_MARKUP = Decimal("1.05")
CENT = Decimal("0.01")

# TWC printed these part-time rates above the full-time rate, as
# (region, provider type, rating, age). No other table has one.
PART_TIME_ABOVE_FULL_TIME = {
    WD_12_18: {
        ("COASTAL_BEND", "LCCH", "REG", "INFANT"),
        ("COASTAL_BEND", "LCCH", "REG", "SCHOOL_AGE"),
        ("COASTAL_BEND", "LCCH", "TRS2", "SCHOOL_AGE"),
        ("COASTAL_BEND", "LCCH", "TRS3", "SCHOOL_AGE"),
        ("COASTAL_BEND", "LCCH", "TRS4", "SCHOOL_AGE"),
        ("COASTAL_BEND", "LCCH", "TSR", "INFANT"),
        ("COASTAL_BEND", "LCCH", "TSR", "SCHOOL_AGE"),
        ("SOUTHEAST", "LCCC", "REG", "INFANT"),
        ("SOUTHEAST", "LCCC", "REG", "TODDLER"),
        ("SOUTHEAST", "LCCC", "TRS2", "INFANT"),
        ("SOUTHEAST", "LCCC", "TSR", "INFANT"),
        ("SOUTHEAST", "LCCC", "TSR", "TODDLER"),
    },
    BCY_2020: {
        ("COASTAL_BEND", "LCCH", "REG", "SCHOOL_AGE"),
        ("COASTAL_BEND", "LCCH", "TRS2", "SCHOOL_AGE"),
        ("COASTAL_BEND", "LCCH", "TSR", "SCHOOL_AGE"),
    },
    BCY_2021: {
        ("COASTAL_BEND", "LCCH", "REG", "SCHOOL_AGE"),
        ("COASTAL_BEND", "LCCH", "TSR", "SCHOOL_AGE"),
    },
}


def _load_cells():
    with open(RATES) as file:
        table = yaml.safe_load(file)
    cells = {}
    for region, by_type in table.items():
        if region in ("description", "metadata"):
            continue
        for provider_type, by_rating in by_type.items():
            for rating, by_age in by_rating.items():
                for age, by_schedule in by_age.items():
                    for schedule, values in by_schedule.items():
                        key = (region, provider_type, rating, age, schedule)
                        cells[key] = values
    return cells


CELLS = _load_cells()
TREE = load_parameter_file(str(RATES), name="rates")


def _with(cell, **changes):
    region, provider_type, rating, age, schedule = cell
    fields = dict(
        region=region,
        provider_type=provider_type,
        rating=rating,
        age=age,
        schedule=schedule,
    )
    fields.update(changes)
    return tuple(fields.values())


def _assert_none(failures):
    assert not failures, f"{len(failures)} cells fail, e.g. {failures[:5]}"


def _floor(regular, markup):
    # TWC rounds some enhanced rates down, so allow a cent below the markup.
    return (Decimal(str(regular)) * markup).quantize(CENT, ROUND_HALF_UP) - CENT


def _tsr_ages(year):
    # §809.20(b)(2) limits the TSR rate to preschool children until the
    # amendment effective October 3, 2022, which adds infants and toddlers.
    # WD 22-22's table, effective October 1, 2022, already prints them.
    if year < BCY_2023:
        return {"PRESCHOOL"}
    return {"INFANT", "TODDLER", "PRESCHOOL"}


def _school_year_blend(full_time, part_time):
    # WD Letter 02-20: the part-day rate for 175 days plus the full-day rate
    # for 30 days, divided by the 205 days of the school year.
    days = Decimal(str(part_time)) * 175 + Decimal(str(full_time)) * 30
    return (days / 205).quantize(CENT, ROUND_HALF_UP)


def _in_force(values, day):
    # The latest table dated on or before the day.
    return values[max(date for date in values if date <= day)]


def _tree_value(cell, day):
    return reduce(lambda node, key: node.children[key], cell, TREE)(day)


def test_every_cell_has_every_year():
    # 28 boards x 16 provider type and rating rows x 9 age and schedule columns.
    assert len(CELLS) == 28 * 16 * 9
    _assert_none(
        [cell for cell, values in CELLS.items() if not set(YEARS) <= set(values)]
    )


@pytest.mark.parametrize("year", YEARS)
def test_texas_rising_star_rates_meet_markups(year):
    failures = []
    for cell, values in CELLS.items():
        markup = TRS_MARKUP.get(cell[2])
        if markup is None:
            continue
        floor = _floor(CELLS[_with(cell, rating="REG")][year], markup)
        if Decimal(str(values[year])) < floor:
            failures.append((cell, values[year], float(floor)))
    _assert_none(failures)


@pytest.mark.parametrize("year", YEARS)
def test_star_levels_rise(year):
    failures = []
    for cell in CELLS:
        if cell[2] != "TRS2":
            continue
        tiers = [CELLS[_with(cell, rating=r)][year] for r in ("TRS2", "TRS3", "TRS4")]
        if tiers != sorted(tiers):
            failures.append((cell, tiers))
    _assert_none(failures)


@pytest.mark.parametrize("year", YEARS)
def test_texas_school_ready_rates(year):
    # A TSR rate for an age group in §809.20(b)(2) meets the 5 percent floor
    # of §809.20(c)(1)(B). From the BCY 2023 table on, each also matches or
    # exceeds the 2-star rate, the minimum TWC set in WD Letter 09-23
    # (June 12, 2023). For other age groups, the tables from WD 12-18 to
    # BCY 2023 give TSR providers the regular rate, while BCY 2024 and
    # BCY 2025 print the 2-star rate.
    failures = []
    for cell, values in CELLS.items():
        if cell[2] != "TSR":
            continue
        regular = CELLS[_with(cell, rating="REG")][year]
        two_star = CELLS[_with(cell, rating="TRS2")][year]
        if cell[3] in _tsr_ages(year):
            meets = Decimal(str(values[year])) >= _floor(regular, TSR_MARKUP)
            if year >= BCY_2023:
                meets = meets and values[year] >= two_star
        elif year < BCY_2024:
            meets = values[year] == regular
        else:
            meets = values[year] == two_star
        if not meets:
            failures.append((cell, values[year], regular))
    _assert_none(failures)


@pytest.mark.parametrize("year", YEARS)
def test_part_time_rates_within_full_time(year):
    # A part-time rate above the full-time rate usually means a value landed
    # in the wrong column, so only the rates TWC printed that way pass.
    above = {
        cell[:4]
        for cell, values in CELLS.items()
        if cell[4] == "PART_TIME"
        and values[year] > CELLS[_with(cell, schedule="FULL_TIME")][year]
    }
    assert above == PART_TIME_ABOVE_FULL_TIME.get(year, set())


@pytest.mark.parametrize("year", YEARS)
def test_blended_rates_between_part_time_and_full_time(year):
    failures = []
    for cell, values in CELLS.items():
        if cell[4] != "BLENDED":
            continue
        rates = [
            CELLS[_with(cell, schedule=s)][year] for s in ("PART_TIME", "FULL_TIME")
        ]
        if not min(rates) <= values[year] <= max(rates):
            failures.append((cell, values[year], rates))
    _assert_none(failures)


@pytest.mark.parametrize("year", YEARS)
def test_blended_rates_follow_school_year_formula(year):
    # WD 23-19, 25-20 and 24-21 print no blended rates, so the table computes
    # them this way. The rates WD 12-18, WD 22-22 and BCY 2025 print match it
    # exactly. WD 20-23 prints 16 of them a cent off.
    tolerance = CENT if year == BCY_2024 else 0
    failures = []
    for cell, values in CELLS.items():
        if cell[4] != "BLENDED":
            continue
        full_time = CELLS[_with(cell, schedule="FULL_TIME")][year]
        part_time = CELLS[_with(cell, schedule="PART_TIME")][year]
        blend = _school_year_blend(full_time, part_time)
        if abs(Decimal(str(values[year])) - blend) > tolerance:
            failures.append((cell, values[year], float(blend)))
    _assert_none(failures)


@pytest.mark.parametrize("earlier, later", list(zip(YEARS, YEARS[1:])))
def test_rates_never_fall(earlier, later):
    # Boards set BCY 2025 relative care rates locally, so those alone may fall.
    failures = [
        (cell, values[earlier], values[later])
        for cell, values in CELLS.items()
        if values[later] < values[earlier]
        and not (cell[1] == "RELATIVE" and later == BCY_2025)
    ]
    _assert_none(failures)


def test_parameter_tree_matches_table_around_each_change():
    # PolicyEngine's parameter loader against the plain YAML read, for every
    # cell on the first day of each table and the day before.
    days = [WD_12_18] + [
        year + offset
        for year in YEARS[1:]
        for offset in (datetime.timedelta(days=-1), datetime.timedelta(0))
    ]
    failures = [
        (cell, day, _tree_value(cell, day), _in_force(values, day))
        for day in days
        for cell, values in CELLS.items()
        if _tree_value(cell, day) != _in_force(values, day)
    ]
    _assert_none(failures)


@settings(deadline=None)
@given(
    cell=st.sampled_from(sorted(CELLS)),
    day=st.dates(min_value=WD_12_18, max_value=datetime.date(2030, 12, 31)),
)
def test_parameter_tree_matches_table_on_any_day(cell, day):
    assert _tree_value(cell, day) == _in_force(CELLS[cell], day)
