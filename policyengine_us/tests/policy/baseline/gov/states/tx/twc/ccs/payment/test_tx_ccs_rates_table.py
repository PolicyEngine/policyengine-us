"""Check the Texas CCS four-age-group rates against TWC's rate rules.

We store eight TWC tables of Board maximum rates in rates.yaml, from TWC's
table of rates as of October 1, 2016 to BCY 2025. Under 40 TAC §809.20(b) and
(c), Boards must set Two-, Three- and Four-Star Texas Rising Star rates at
least 5, 7 and 9 percent above the regular rate. They must set Texas School
Ready (TSR) rates at least 5 percent above it for the age groups in
§809.20(b)(2). Under (d), they may set Texas Rising Star rates higher if each
star level exceeds the one below by at least 2 percentage points. Every
full-time and part-time rate in the eight tables clears these floors with no
rounding allowance, and so does every school-age blended rate in BCY 2020,
BCY 2021, revised BCY 2024 and BCY 2025. In the October 2016 table, two South
Texas TSR rates clear their floor only because we raise them to it in
rates.yaml. Every blended rate but one follows the school-year formula in
WD Letter 02-20 from its own part-time and full-time rates, so after rounding
to the cent some fall under a cent short of a floor or star gap. We count 30
such shortfalls in the October 2016 table, 4 in WD 12-18, 56 in BCY 2022 and 63
in BCY 2023. In the August 29, 2023 original of the BCY 2024 table, TWC printed
some rates that fall less than a cent short of a markup floor or star gap, and
these checks fail on them.

In each rate letter from WD 12-18 to WD 20-23, TWC said it would cut no
provider's rate in setting the new rates. Outside relative care, TWC kept each
BCY 2025 rate at or above its BCY 2024 level, under the method its Commission
approved on September 10, 2024 (WD Letter 19-24, Change 1, pp. 1-2). TWC sets
no minimum for relative care rates, and Boards may set them locally (p. 3).
Across the eight tables, TWC printed a rate below the previous table's only in
the four cells FALLS lists.

TWC also followed two patterns that no rule requires. It printed each TSR rate
for the §809.20(b)(2) age groups equal to the Two-Star rate from BCY 2023 on,
and every TSR rate from BCY 2024 on, school age included, although under
§809.20(b)(2), Boards set TSR rates only for infants, toddlers and
preschoolers. Outside relative care, each blended rate lies strictly between
its part-time and full-time rates, and each part-time rate lies below its
full-time rate except in the cells PART_TIME_ABOVE_FULL_TIME and
EQUAL_PART_AND_FULL_TIME list. The tests check both patterns.

Each check runs over all 4,032 cells of the eight tables. A test fails when
someone types a value into the wrong cell and the value breaks one of these
bounds. Outside relative care, copying a part-time rate into a full-time cell
breaks one whenever the copy changes the value. The checks can still pass if
someone types a regular rate too low or a Three- or Four-Star rate too high, or
copies a rate from another age group. They check relative care rates only for
schedule order, the school-age blended formula and falls from one table to the
next, so a typo in one can pass. So can a part-time rate copied into the
full-time cell for a younger child in the October 2016 table, where the tests
have no earlier rate to compare it with. The YAML tests pin single cells to
TWC's tables.
"""

import datetime
import operator
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

OCT_2016 = datetime.date(2016, 10, 1)
WD_12_18 = datetime.date(2018, 8, 1)
BCY_2020 = datetime.date(2019, 10, 1)
BCY_2021 = datetime.date(2020, 10, 1)
BCY_2022 = datetime.date(2021, 10, 1)
BCY_2023 = datetime.date(2022, 10, 1)
BCY_2024 = datetime.date(2023, 10, 1)
BCY_2025 = datetime.date(2024, 10, 1)
YEARS = [
    OCT_2016,
    WD_12_18,
    BCY_2020,
    BCY_2021,
    BCY_2022,
    BCY_2023,
    BCY_2024,
    BCY_2025,
]

MARKUP = {
    "TRS2": Decimal("1.05"),
    "TSR": Decimal("1.05"),
    "TRS3": Decimal("1.07"),
    "TRS4": Decimal("1.09"),
}
STAR_GAP = Decimal("0.02")
CENT = Decimal("0.01")

# How many times an enhanced school-age blended rate falls under a cent short
# of a floor or star gap after rounding, by table. The formula test pins every
# blended rate to its own part-time and full-time rates, so the shortfalls hide
# no other error.
BLENDED_SHORT = {OCT_2016: 30, WD_12_18: 4, BCY_2022: 56, BCY_2023: 63}

EVERY_RATING = {"REG", "TRS2", "TRS3", "TRS4", "TSR"}

# Part-time rates above the full-time rate, as (region, provider type, rating,
# age). TWC printed all but the October 2016 TSR rates, all outside preschool,
# and the Coastal Bend LCCH TSR school-age rates in BCY 2020 and BCY 2021,
# which we copy from the regular rates under the TSR rule. No other table has
# one.
PART_TIME_ABOVE_FULL_TIME = {
    OCT_2016: {
        (region, provider_type, rating, age)
        for region, provider_type, ages in (
            ("COASTAL_BEND", "LCCH", ("INFANT", "SCHOOL_AGE")),
            ("SOUTHEAST", "LCCC", ("INFANT", "TODDLER")),
        )
        for rating in EVERY_RATING
        for age in ages
    },
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

# Part-time rates equal to the full-time rate, as (region, provider type, age)
# and the ratings that tie. TWC printed each tie, except the TSR ties we copy
# from a tied regular rate under the TSR rule. No other table has one.
CONCHO_VALLEY_HOME_INFANTS = {
    ("CONCHO_VALLEY", provider_type, "INFANT"): EVERY_RATING
    for provider_type in ("LCCH", "RCCH")
}
EQUAL_PART_AND_FULL_TIME = {
    OCT_2016: {
        **{
            group: EVERY_RATING
            for group in (
                ("CAMERON_COUNTY", "LCCH", "INFANT"),
                ("CAMERON_COUNTY", "LCCH", "TODDLER"),
                ("CAMERON_COUNTY", "LCCH", "PRESCHOOL"),
                ("CONCHO_VALLEY", "LCCC", "INFANT"),
                ("CONCHO_VALLEY", "LCCH", "INFANT"),
                ("CONCHO_VALLEY", "RCCH", "INFANT"),
                ("DEEP_EAST", "LCCC", "INFANT"),
                ("DEEP_EAST", "RCCH", "INFANT"),
                ("DEEP_EAST", "RCCH", "TODDLER"),
                ("HEART_OF_TEXAS", "LCCH", "INFANT"),
                ("HEART_OF_TEXAS", "LCCH", "TODDLER"),
                ("HEART_OF_TEXAS", "RCCH", "INFANT"),
                ("SOUTHEAST", "LCCH", "INFANT"),
            )
        },
        ("HEART_OF_TEXAS", "RCCH", "PRESCHOOL"): {"TRS4"},
        ("LOWER_RIO", "LCCH", "TODDLER"): {"TRS2"},
    },
    WD_12_18: {
        ("CAMERON_COUNTY", "LCCH", "INFANT"): {"REG", "TSR"},
        ("CAMERON_COUNTY", "LCCH", "TODDLER"): {"REG", "TSR"},
        ("CAMERON_COUNTY", "LCCH", "PRESCHOOL"): {"REG", "TSR"},
        ("CONCHO_VALLEY", "LCCC", "INFANT"): EVERY_RATING,
        ("CONCHO_VALLEY", "LCCH", "INFANT"): EVERY_RATING,
        ("CONCHO_VALLEY", "RCCH", "INFANT"): EVERY_RATING,
        ("DEEP_EAST", "LCCC", "INFANT"): {"REG", "TRS2", "TSR"},
        ("DEEP_EAST", "RCCH", "INFANT"): {"REG", "TSR"},
        ("DEEP_EAST", "RCCH", "TODDLER"): {"REG", "TSR"},
        ("HEART_OF_TEXAS", "LCCH", "INFANT"): {"REG", "TSR"},
        ("HEART_OF_TEXAS", "LCCH", "TODDLER"): {"REG", "TRS2", "TSR"},
        ("HEART_OF_TEXAS", "RCCH", "INFANT"): {"REG", "TRS2", "TSR"},
        ("SOUTHEAST", "LCCH", "INFANT"): {"REG", "TSR"},
    },
    BCY_2020: {
        ("CONCHO_VALLEY", provider_type, "INFANT"): EVERY_RATING
        for provider_type in ("LCCC", "LCCH", "RCCH")
    },
    BCY_2021: {
        ("CONCHO_VALLEY", "LCCC", "INFANT"): {"REG", "TRS2", "TRS3", "TSR"},
        **CONCHO_VALLEY_HOME_INFANTS,
    },
    BCY_2022: CONCHO_VALLEY_HOME_INFANTS,
    BCY_2023: CONCHO_VALLEY_HOME_INFANTS,
    BCY_2024: CONCHO_VALLEY_HOME_INFANTS,
}

# TWC printed this blended rate at $12.21, where the school-year formula gives
# $12.12, the rate TWC printed for BCY 2025. No other printed blended rate
# misses the formula.
BLENDED_OFF_FORMULA = {
    BCY_2024: {("EAST_TEXAS", "RELATIVE", "NONE", "SCHOOL_AGE")},
}

# Rates below the previous table's rate. In WD 12-18, TWC set each full-time
# and part-time TSR preschool rate at the greater of 105 percent of the new
# regular rate and the Board's current TSR rate. It printed these three Lower
# Rio Grande Valley rates at 105 percent, rounded up to the cent, below its
# October 2016 rates. In WD 27-16, TWC had Boards suspend rate increases and
# said nothing of cuts, so the Board may have lowered them after October 2016.
# In BCY 2025, TWC printed the formula's $12.12 for the East Texas relative
# care blended rate, below the $12.21 it printed for BCY 2024. In
# WD Letter 19-24, Change 1, TWC set no minimum for relative care rates.
FALLS = {
    WD_12_18: {
        ("LOWER_RIO", "LCCH", "TSR", "PRESCHOOL", "FULL_TIME"),
        ("LOWER_RIO", "LCCH", "TSR", "PRESCHOOL", "PART_TIME"),
        ("LOWER_RIO", "RCCH", "TSR", "PRESCHOOL", "PART_TIME"),
    },
    BCY_2025: {("EAST_TEXAS", "RELATIVE", "NONE", "SCHOOL_AGE", "BLENDED")},
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
    # Under §809.20(b)(2), Boards set TSR rates for preschool children alone
    # until TWC added infants and toddlers in an amendment effective
    # October 3, 2022. TWC already printed their TSR rates in WD 22-22's table,
    # effective October 1, 2022.
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
    # 28 Boards x 16 provider type and rating rows x 9 age and schedule
    # columns, each with values on the eight table dates and no others. An
    # extra date would change the rate for the months until the next table.
    assert len(CELLS) == 28 * 16 * 9
    _assert_none([cell for cell, values in CELLS.items() if set(values) != set(YEARS)])


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
        check
        for check in chain(_floors(year), _star_gaps(year))
        if check[0][4] == "BLENDED" and check[1] < check[2]
    ]
    assert len(short) == BLENDED_SHORT.get(year, 0)


@pytest.mark.parametrize("year", YEARS)
def test_texas_school_ready_rates(year):
    # TWC printed each TSR rate for an age group in §809.20(b)(2) equal to the
    # Two-Star rate from BCY 2023, and every TSR rate from BCY 2024. No rule
    # requires equality: in WD Letter 09-23, effective June 12, 2023, partway
    # through the BCY 2023 table's year, TWC set the Two-Star rate as the
    # minimum for those age groups. Through BCY 2023, TSR providers get the
    # regular rate for other age groups. TWC printed it in every such cell of
    # WD 12-18 and in eight later ones, six in WD 25-20 and two in WD 24-21.
    # For the rest, we supply it in rates.yaml under the TSR fill rule, since
    # TWC left them blank or dashed or, in the October 2016 table, printed TSR
    # rates for preschool only. Before BCY 2023, the markup test checks the
    # preschool TSR floor.
    failures = []
    for cell in CELLS:
        if cell[2] != "TSR" or (year < BCY_2023 and cell[3] in _tsr_ages(year)):
            continue
        two_star = year >= BCY_2024 or cell[3] in _tsr_ages(year)
        expected = _rate(cell, year, rating="TRS2" if two_star else "REG")
        if _rate(cell, year) != expected:
            failures.append((cell, _rate(cell, year), expected))
    _assert_none(failures)


def _expand(groups):
    return {
        (region, provider_type, rating, age)
        for (region, provider_type, age), ratings in groups.items()
        for rating in ratings
    }


@pytest.mark.parametrize("year", YEARS)
def test_part_time_rates_below_full_time(year):
    # No rule requires this ordering, but outside relative care each part-time
    # rate lies below the full-time rate except in the cells listed above, so a
    # part-time rate at or above the full-time rate points to a value in the
    # wrong column. Some Boards pay relative care the same for both schedules,
    # so the test allows equal rates there. Outside relative care, the test
    # requires a part-time rate at or above the full-time rate in each listed
    # cell and in no other.
    above, equal, relative = set(), set(), []
    for cell in CELLS:
        if cell[4] != "PART_TIME":
            continue
        part_time = _rate(cell, year)
        full_time = _rate(cell, year, schedule="FULL_TIME")
        if cell[1] == "RELATIVE":
            if part_time > full_time:
                relative.append((cell, part_time, full_time))
        elif part_time > full_time:
            above.add(cell[:4])
        elif part_time == full_time:
            equal.add(cell[:4])
    _assert_none(relative)
    assert above == PART_TIME_ABOVE_FULL_TIME.get(year, set())
    assert equal == _expand(EQUAL_PART_AND_FULL_TIME.get(year, {}))


@pytest.mark.parametrize("year", YEARS)
def test_blended_rates_between_part_time_and_full_time(year):
    # Outside relative care, each blended rate falls strictly between its
    # part-time and full-time rates.
    failures = []
    for cell in CELLS:
        if cell[4] != "BLENDED":
            continue
        low, high = sorted(
            _rate(cell, year, schedule=s) for s in ("PART_TIME", "FULL_TIME")
        )
        below = operator.le if cell[1] == "RELATIVE" else operator.lt
        if not (below(low, _rate(cell, year)) and below(_rate(cell, year), high)):
            failures.append((cell, low, _rate(cell, year), high))
    _assert_none(failures)


@pytest.mark.parametrize("year", YEARS)
def test_blended_rates_follow_school_year_formula(year):
    # TWC printed no blended rates in its October 2016 table or in WD 23-19,
    # 25-20 and 24-21, so we compute them this way.
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
    falls = {cell for cell, values in CELLS.items() if values[later] < values[earlier]}
    assert falls == FALLS.get(later, set())


def test_parameter_tree_matches_table_around_each_change():
    # PolicyEngine's parameter loader against the plain YAML read, for every
    # cell on the first day of each table and, after the first table, the day
    # before.
    days = [YEARS[0]] + [
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
    day=st.dates(min_value=YEARS[0], max_value=datetime.date(2030, 12, 31)),
)
def test_parameter_tree_matches_table_on_any_day(cell, day):
    assert _tree_value(cell, day) == _in_force(CELLS[cell], day)
