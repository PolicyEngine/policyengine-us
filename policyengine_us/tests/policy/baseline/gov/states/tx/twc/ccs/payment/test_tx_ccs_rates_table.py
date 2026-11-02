"""The Texas CCS four-age-group rate table obeys the rules that set it.

40 TAC §809.20(c)-(d) sets Texas Rising Star rates at least 5, 7 and 9
percent above a provider's regular rate. WD Letter 19-24, Change 1, keeps
every BCY 2025 rate at or above its BCY 2024 level, except relative care,
which Boards set locally. Each check runs over all 4,032 cells of both board
contract years, so a value copied into the wrong cell fails here. The test
reads the YAML file directly and builds no tax-benefit system.
"""

import datetime
from decimal import ROUND_HALF_UP, Decimal
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

TRS_MARKUP = {
    "TRS2": Decimal("1.05"),
    "TRS3": Decimal("1.07"),
    "TRS4": Decimal("1.09"),
}
CENT = Decimal("0.01")


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


def _assert_none(failures):
    assert not failures, f"{len(failures)} cells fail, e.g. {failures[:5]}"


def test_every_cell_has_both_years():
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
        regular = Decimal(str(CELLS[_with(cell, rating="REG")][year]))
        floor = (regular * markup).quantize(CENT, ROUND_HALF_UP) - CENT
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
