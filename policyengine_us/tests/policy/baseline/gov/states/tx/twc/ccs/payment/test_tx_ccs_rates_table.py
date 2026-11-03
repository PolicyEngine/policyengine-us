"""The Texas CCS four-age-group rate table obeys the rules that set it.

The table holds seven statewide TWC tables, from WD Letter 12-18 (effective
August 1, 2018) to BCY 2025. Under 40 TAC §809.20(c), Texas Rising Star rates
must exceed a provider's regular rate by at least 5, 7 and 9 percent, and a
Texas School Ready (TSR) rate must exceed it by at least 5 percent for the age
groups in §809.20(b)(2). Under §809.20(d), Boards may go higher if each star
level stays at least 2 percentage points above the one below. Every full-time
and part-time rate meets these bounds exactly, and so does every school-age
blended rate for BCY 2020, BCY 2021, revised BCY 2024 and BCY 2025. Each
blended rate follows WD 02-20's formula from its own part-time and full-time
rates, so in WD 12-18, BCY 2022 and BCY 2023 rounding leaves enhanced blended
rates under a cent short of a bound 4, 56 and 63 times. In the August 29, 2023
original of the BCY 2024 table, hundreds of rates miss the bounds by under a
cent, so these checks also tell its two versions apart. In each rate letter
from WD 12-18 to WD 20-23, TWC says it will reduce no provider rate, and in WD
Letter 19-24, Change 1, TWC keeps every BCY 2025 rate at or above its BCY 2024
level, except relative care, which Boards set locally. Each check runs over all
4,032 cells of every table, so a value copied into the wrong cell fails here.
The test reads the YAML file directly and builds no tax-benefit system.
"""

import datetime
from decimal import ROUND_HALF_UP, Decimal
from functools import reduce
from itertools import chain
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

MARKUP = {
    "TRS2": Decimal("1.05"),
    "TSR": Decimal("1.05"),
    "TRS3": Decimal("1.07"),
    "TRS4": Decimal("1.09"),
}
STAR_GAP = Decimal("0.02")
CENT = Decimal("0.01")

# How many times rounding leaves an enhanced school-age blended rate under a
# cent short of a floor or star gap, by table. The formula test pins every
# blended rate to its own part-time and full-time rates, so the shortfalls hide
# no other error.
BLENDED_SHORT = {WD_12_18: 4, BCY_2022: 56, BCY_2023: 63}

# Part-time rates above the full-time rate, as (region, provider type, rating,
# age). TWC printed all but the Coastal Bend LCCH TSR school-age rates in
# BCY 2020 and BCY 2021, which we copy from the regular rates under the TSR
# rule. No other table has one.
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

# TWC printed this blended rate at $12.21, where the school-year formula and
# the BCY 2025 table give $12.12. No other printed blended rate misses it.
BLENDED_OFF_FORMULA = {
    BCY_2024: {("EAST_TEXAS", "RELATIVE", "NONE", "SCHOOL_AGE")},
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


def _rate(cell, year, **changes):
    return Decimal(str(CELLS[_with(cell, **changes)][year]))


def _meets(cell, amount, bound, year):
    if cell[4] == "BLENDED" and year in BLENDED_SHORT:
        return amount > bound - CENT
    return amount >= bound


def _assert_none(failures):
    assert not failures, f"{len(failures)} cells fail, e.g. {failures[:5]}"


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
    return ((part_time * 175 + full_time * 30) / 205).quantize(CENT, ROUND_HALF_UP)


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


def _floors(year):
    # Each enhanced rate and its §809.20(c) floor. A TSR rate has a floor only
    # for the age groups in §809.20(b)(2).
    for cell in CELLS:
        markup = MARKUP.get(cell[2])
        if markup is None or (cell[2] == "TSR" and cell[3] not in _tsr_ages(year)):
            continue
        yield cell, _rate(cell, year), _rate(cell, year, rating="REG") * markup


def _star_gaps(year):
    # Each star level's rise over the level below it and the §809.20(d) gap,
    # 2 percent of the regular rate, under the higher level's cell.
    for cell in CELLS:
        if cell[2] != "TRS2":
            continue
        gap = STAR_GAP * _rate(cell, year, rating="REG")
        for lower, higher in (("TRS2", "TRS3"), ("TRS3", "TRS4")):
            rise = _rate(cell, year, rating=higher) - _rate(cell, year, rating=lower)
            yield _with(cell, rating=higher), rise, gap


@pytest.mark.parametrize("year", YEARS)
def test_enhanced_rates_meet_markups(year):
    _assert_none([check for check in _floors(year) if not _meets(*check, year)])


@pytest.mark.parametrize("year", YEARS)
def test_star_levels_two_points_apart(year):
    _assert_none([check for check in _star_gaps(year) if not _meets(*check, year)])


@pytest.mark.parametrize("year", YEARS)
def test_blended_shortfalls_match_their_count(year):
    short = [
        check for check in chain(_floors(year), _star_gaps(year)) if check[1] < check[2]
    ]
    assert len(short) == BLENDED_SHORT.get(year, 0)


@pytest.mark.parametrize("year", YEARS)
def test_texas_school_ready_rates(year):
    # From the BCY 2023 table on, a TSR rate for an age group in §809.20(b)(2)
    # matches or exceeds the 2-star rate, the minimum TWC set in WD Letter
    # 09-23 (June 12, 2023). For other age groups, the tables from WD 12-18 to
    # BCY 2023 give TSR providers the regular rate, while BCY 2024 and
    # BCY 2025 print the 2-star rate.
    failures = []
    for cell in CELLS:
        if cell[2] != "TSR":
            continue
        rate = _rate(cell, year)
        if cell[3] in _tsr_ages(year):
            meets = year < BCY_2023 or rate >= _rate(cell, year, rating="TRS2")
        elif year < BCY_2024:
            meets = rate == _rate(cell, year, rating="REG")
        else:
            meets = rate == _rate(cell, year, rating="TRS2")
        if not meets:
            failures.append((cell, float(rate)))
    _assert_none(failures)


@pytest.mark.parametrize("year", YEARS)
def test_part_time_rates_within_full_time(year):
    # A part-time rate above the full-time rate usually means a value landed
    # in the wrong column, so only the rates TWC printed that way pass.
    above = {
        cell[:4]
        for cell in CELLS
        if cell[4] == "PART_TIME"
        and _rate(cell, year) > _rate(cell, year, schedule="FULL_TIME")
    }
    assert above == PART_TIME_ABOVE_FULL_TIME.get(year, set())


@pytest.mark.parametrize("year", YEARS)
def test_blended_rates_between_part_time_and_full_time(year):
    failures = []
    for cell in CELLS:
        if cell[4] != "BLENDED":
            continue
        rates = [_rate(cell, year, schedule=s) for s in ("PART_TIME", "FULL_TIME")]
        if not min(rates) <= _rate(cell, year) <= max(rates):
            failures.append((cell, float(_rate(cell, year)), rates))
    _assert_none(failures)


@pytest.mark.parametrize("year", YEARS)
def test_blended_rates_follow_school_year_formula(year):
    # WD 23-19, 25-20 and 24-21 print no blended rates, so the table computes
    # them this way.
    off = {
        cell[:4]
        for cell in CELLS
        if cell[4] == "BLENDED"
        and _rate(cell, year)
        != _school_year_blend(
            _rate(cell, year, schedule="FULL_TIME"),
            _rate(cell, year, schedule="PART_TIME"),
        )
    }
    assert off == BLENDED_OFF_FORMULA.get(year, set())


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
