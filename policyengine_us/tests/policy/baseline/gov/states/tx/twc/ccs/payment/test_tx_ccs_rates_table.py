"""Check the Texas CCS four-age-group rates against TWC's rate rules.

Under 40 TAC §809.20(c), Boards must set Texas Rising Star rates at least 5, 7
and 9 percent above the regular rate. Under (d), they may set them higher if
each star level exceeds the one below by at least 2 percentage points. TWC
tiers Texas School Ready rates under the same rule (WD Letter 20-23). Every
rate in TWC's revised BCY 2024 table (October 16, 2023) and its BCY 2025 table
clears these floors with no rounding allowance. The August 29, 2023 original
misses both floors by under a cent in some cells, and these checks fail on its
values. For BCY 2025, TWC's Commission kept every rate at or above its BCY 2024
level, except relative care rates, which Boards set locally (WD Letter 19-24,
Change 1).

In both tables, TWC also followed two patterns that no rule requires. It
printed each Texas School Ready rate equal to the Two-Star rate. Outside
relative care, it printed each part-time rate below the full-time rate and each
blended rate between the two, except in the cells EQUAL_PART_AND_FULL_TIME
lists. The tests check both patterns.

Each check runs over all 4,032 cells of both board contract years. A test fails
when a value typed into the wrong cell breaks one of these bounds, as a
part-time rate copied into a full-time cell does. The checks can still pass a
regular rate typed too low, or a Three- or Four-Star rate typed too high. The
YAML tests pin single cells to TWC's tables. This test reads the YAML file
directly and builds no tax-benefit system.
"""

import datetime
import operator
from decimal import Decimal
from pathlib import Path

import pytest
import yaml

PACKAGE = next(
    parent
    for parent in Path(__file__).resolve().parents
    if parent.name == "policyengine_us"
)
RATES = PACKAGE / "parameters/gov/states/tx/twc/ccs/payment/rates.yaml"

BCY_2024 = datetime.date(2023, 10, 1)
BCY_2025 = datetime.date(2024, 10, 1)
YEARS = [BCY_2024, BCY_2025]

MARKUP = {
    "TRS2": Decimal("1.05"),
    "TSR": Decimal("1.05"),
    "TRS3": Decimal("1.07"),
    "TRS4": Decimal("1.09"),
}
STAR_GAP = Decimal("0.02")

# In its BCY 2024 table, TWC printed the same part-time and full-time rate for
# Concho Valley's home-based infant care at every rating. Each key is
# (year, region, provider type, age).
EQUAL_PART_AND_FULL_TIME = {
    (BCY_2024, "CONCHO_VALLEY", provider_type, "INFANT")
    for provider_type in ("LCCH", "RCCH")
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


def _assert_none(failures):
    assert not failures, f"{len(failures)} cells fail, e.g. {failures[:5]}"


def test_every_cell_has_both_years():
    # 28 boards x 16 provider type and rating rows x 9 age and schedule columns.
    assert len(CELLS) == 28 * 16 * 9
    _assert_none(
        [cell for cell, values in CELLS.items() if not set(YEARS) <= set(values)]
    )


@pytest.mark.parametrize("year", YEARS)
def test_enhanced_rates_meet_markups(year):
    failures = []
    for cell in CELLS:
        markup = MARKUP.get(cell[2])
        if markup is None:
            continue
        floor = _rate(cell, year, rating="REG") * markup
        if _rate(cell, year) < floor:
            failures.append((cell, float(_rate(cell, year)), float(floor)))
    _assert_none(failures)


@pytest.mark.parametrize("year", YEARS)
def test_star_levels_two_points_apart(year):
    failures = []
    for cell in CELLS:
        if cell[2] != "TRS2":
            continue
        regular = _rate(cell, year, rating="REG")
        tiers = [_rate(cell, year, rating=r) for r in ("TRS2", "TRS3", "TRS4")]
        if any(
            higher - lower < STAR_GAP * regular
            for lower, higher in zip(tiers, tiers[1:])
        ):
            failures.append((cell, float(regular), [float(t) for t in tiers]))
    _assert_none(failures)


@pytest.mark.parametrize("year", YEARS)
def test_part_time_and_blended_rates_within_full_time(year):
    # No rule requires this ordering, but TWC printed both tables this way, so
    # a part-time rate at or above the full-time rate points to a value in the
    # wrong column. Some Boards pay relative care the same for both schedules,
    # and TWC printed equal rates for the cells in EQUAL_PART_AND_FULL_TIME, so
    # those get the non-strict check.
    failures = []
    for cell, values in CELLS.items():
        region, provider_type, _, age, schedule = cell
        tied = (year, region, provider_type, age) in EQUAL_PART_AND_FULL_TIME
        below = operator.le if tied or provider_type == "RELATIVE" else operator.lt
        full_time = CELLS[_with(cell, schedule="FULL_TIME")][year]
        if schedule == "PART_TIME" and not below(values[year], full_time):
            failures.append((cell, values[year], full_time))
        if schedule == "PART_TIME" and tied and values[year] != full_time:
            failures.append(("listed as equal", cell, values[year], full_time))
        if schedule == "BLENDED":
            part_time = CELLS[_with(cell, schedule="PART_TIME")][year]
            if not (below(part_time, values[year]) and below(values[year], full_time)):
                failures.append((cell, part_time, values[year], full_time))
    _assert_none(failures)


@pytest.mark.parametrize("year", YEARS)
def test_school_ready_rates_equal_two_star_rates(year):
    # Under §809.20(c), Boards need only set Texas School Ready rates at least
    # 5 percent above the regular rate, but TWC printed each one equal to the
    # Two-Star rate in both tables.
    failures = [
        (cell, values[year], CELLS[_with(cell, rating="TRS2")][year])
        for cell, values in CELLS.items()
        if cell[2] == "TSR" and values[year] != CELLS[_with(cell, rating="TRS2")][year]
    ]
    _assert_none(failures)


def test_bcy_2025_rates_keep_bcy_2024_levels():
    failures = [
        (cell, values[BCY_2024], values[BCY_2025])
        for cell, values in CELLS.items()
        if cell[1] != "RELATIVE" and values[BCY_2025] < values[BCY_2024]
    ]
    _assert_none(failures)
