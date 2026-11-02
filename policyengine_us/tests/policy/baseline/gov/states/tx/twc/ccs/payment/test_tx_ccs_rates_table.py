"""The Texas CCS four-age-group rate table obeys the rules that set it.

40 TAC §809.20(c) sets Texas Rising Star rates at least 5, 7 and 9 percent
above a provider's regular rate, and (d) lets Boards go higher if each star
level stays at least 2 percentage points above the one below. WD Letter 20-23
tiers Texas School Ready rates under the same rule, and the tables set them
equal to Two-Star rates. TWC's revised BCY 2024 table (October 16, 2023) and
its BCY 2025 table meet these bounds exactly, with no rounding allowance. The
August 29, 2023 original misses both by under a cent in some cells, so these
checks also tell the two versions apart. WD Letter 19-24, Change 1, keeps every
BCY 2025 rate at or above its BCY 2024 level, except relative care, which
Boards set locally. Each check runs over all 4,032 cells of both board contract
years, so a value copied into the wrong cell fails here. The test reads the
YAML file directly and builds no tax-benefit system.
"""

import datetime
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
    # Not a rule, but true of every TWC table: a part-time rate above the
    # full-time rate means a value landed in the wrong column.
    failures = []
    for cell, values in CELLS.items():
        full_time = CELLS[_with(cell, schedule="FULL_TIME")][year]
        if cell[4] == "PART_TIME" and values[year] > full_time:
            failures.append((cell, values[year], full_time))
        if cell[4] == "BLENDED":
            part_time = CELLS[_with(cell, schedule="PART_TIME")][year]
            if not part_time <= values[year] <= full_time:
                failures.append((cell, part_time, values[year], full_time))
    _assert_none(failures)


def test_bcy_2025_rates_keep_bcy_2024_levels():
    failures = [
        (cell, values[BCY_2024], values[BCY_2025])
        for cell, values in CELLS.items()
        if cell[1] != "RELATIVE" and values[BCY_2025] < values[BCY_2024]
    ]
    _assert_none(failures)
