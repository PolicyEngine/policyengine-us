"""The Texas CCS expanded-age rate tables obey the rules that set them.

40 TAC §809.20(c) sets Texas Rising Star rates at least 5, 7 and 9 percent above
a provider's regular rate, and (d) keeps each star level at least 2 percentage
points above the one below. TWC's tables give Texas School Ready providers the
Two-Star rate. WD Letter 02-20 sets the blended rate at (175 x part-time + 30 x
full-time) / 205, and TWC's printed rates round it half up to the cent. WD Letter
08-25 keeps each BCY 2026 rate at or above its BCY 2025 level, except relative
care, which Boards set locally. WD Letter 19-24, Change 1, bases each four-age
rate on the lowest eight-age rate in its group.

Each check runs over all 8,512 cells of bcy2025.csv and bcy2026.csv. The checks
need TWC's rules and the four-age table, not its eight-age PDFs, so a value that
satisfies them can still differ from what TWC printed. Only the lookup tests build
the tax-benefit system.
"""

import csv
import datetime
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import numpy as np
import pytest
import yaml
from hypothesis import given, settings
from hypothesis import strategies as st

PACKAGE = next(
    parent
    for parent in Path(__file__).resolve().parents
    if parent.name == "policyengine_us"
)
PAYMENT = PACKAGE / "parameters/gov/states/tx/twc/ccs/payment"
TABLE_FOLDER = PAYMENT / "rates_expanded_age_groups"

BOARDS = 28
ROWS_PER_BOARD = 16
AGES = ["0_11m", "12_17m", "18_23m", "2yr", "3yr", "4yr", "5yr", "6_13yr"]
BLENDED_AGES = ["4yr", "5yr", "6_13yr"]
COLUMNS = [f"age_{age}_{schedule}" for age in AGES for schedule in ("ft", "pt")] + [
    f"age_{age}_bt" for age in BLENDED_AGES
]

MARKUP = {
    "TRS2": Decimal("1.05"),
    "TSR": Decimal("1.05"),
    "TRS3": Decimal("1.07"),
    "TRS4": Decimal("1.09"),
}
STAR_GAP = Decimal("0.02")
CENT = Decimal("0.01")

# Blended rates for ages 4 and 5 have no BCY 2025 printing to round to the markup,
# so WD Letter 02-20's formula alone sets them. Rounding leaves six of them under a
# cent short of 1.05 x the regular blended rate. Their full-time and part-time rates
# meet the markup exactly.
DERIVED_BLENDED_2025 = {"age_4yr_bt", "age_5yr_bt"}

# WD Letter 19-24, Change 1: the four age groups and the eight they cover.
FOUR_AGE_GROUP = {
    "0_11m": "INFANT",
    "12_17m": "INFANT",
    "18_23m": "TODDLER",
    "2yr": "TODDLER",
    "3yr": "PRESCHOOL",
    "4yr": "PRESCHOOL",
    "5yr": "PRESCHOOL",
    "6_13yr": "SCHOOL_AGE",
}
FOUR_AGE_DATE = datetime.date(2024, 10, 1)
SCHEDULE = {"ft": "FULL_TIME", "pt": "PART_TIME", "bt": "BLENDED"}

# PR 10598 corrects these rates.yaml cells to TWC's four-age table. The test skips
# a cell only while it holds the uncorrected value.
UNCORRECTED_FOUR_AGE = {
    ("DALLAS_COUNTY", "LCCC", "TRS4", "INFANT", "PART_TIME"): Decimal("45.45"),
    ("DALLAS_COUNTY", "LCCH", "TRS3", "SCHOOL_AGE", "FULL_TIME"): Decimal("38.65"),
    ("DALLAS_COUNTY", "RCCH", "REG", "INFANT", "PART_TIME"): Decimal("37.00"),
    ("DALLAS_COUNTY", "RCCH", "REG", "SCHOOL_AGE", "FULL_TIME"): Decimal("36.50"),
}

# The only relative rates that change from BCY 2025 to BCY 2026.
RELATIVE_CHANGES_IN_BCY_2026 = {
    ("BRAZOS_VALLEY", "age_6_13yr_pt"): (Decimal("5.35"), Decimal("5.23")),
    ("BRAZOS_VALLEY", "age_6_13yr_bt"): (Decimal("6.10"), Decimal("6.00")),
}


def _load_table(year):
    table = {}
    with open(TABLE_FOLDER / f"bcy{year}.csv", newline="") as file:
        for row in csv.DictReader(file):
            key = (row["region"], row["provider_type"], row["provider_rating"])
            assert key not in table, key
            table[key] = {column: Decimal(row[column]) for column in COLUMNS}
    return table


TABLES = {2025: _load_table(2025), 2026: _load_table(2026)}
YEARS = sorted(TABLES)


def _load_four_age():
    with open(PAYMENT / "rates.yaml") as file:
        return yaml.safe_load(file)


FOUR_AGE = _load_four_age()


def _four_age_rate(region, provider_type, rating, group, schedule):
    return Decimal(
        str(FOUR_AGE[region][provider_type][rating][group][schedule][FOUR_AGE_DATE])
    )


def _regulated(table):
    return [key for key in table if key[1] != "RELATIVE"]


def _half_up(value):
    return value.quantize(CENT, ROUND_HALF_UP)


def _assert_none(failures):
    assert not failures, f"{len(failures)} cells fail, e.g. {failures[:5]}"


@pytest.mark.parametrize("year", YEARS)
def test_every_board_has_every_row_and_cell(year):
    table = TABLES[year]
    assert len(table) == BOARDS * ROWS_PER_BOARD
    assert len(table) * len(COLUMNS) == 8_512
    regions = {key[0] for key in table}
    assert len(regions) == BOARDS
    rows = {key[1:] for key in table}
    assert rows == {
        (provider_type, rating)
        for provider_type in ("LCCC", "LCCH", "RCCH")
        for rating in ("REG", "TRS2", "TRS3", "TRS4", "TSR")
    } | {("RELATIVE", "REG")}


def test_both_years_list_the_same_rows_in_the_same_order():
    assert list(TABLES[2025]) == list(TABLES[2026])


@pytest.mark.parametrize("year", YEARS)
def test_enhanced_rates_meet_markups(year):
    table = TABLES[year]
    failures = []
    for key in _regulated(table):
        region, provider_type, rating = key
        markup = MARKUP.get(rating)
        if markup is None:
            continue
        regular = table[(region, provider_type, "REG")]
        for column in COLUMNS:
            floor = regular[column] * markup
            if year == 2025 and column in DERIVED_BLENDED_2025:
                floor -= CENT
            if table[key][column] < floor:
                failures.append((key, column, table[key][column], floor))
    _assert_none(failures)


def test_derived_blended_shortfalls_stay_as_counted():
    # Pins the allowance above: six cells, each under a cent short.
    table = TABLES[2025]
    shortfalls = []
    for key in _regulated(table):
        region, provider_type, rating = key
        markup = MARKUP.get(rating)
        if markup is None:
            continue
        for column in DERIVED_BLENDED_2025:
            floor = table[(region, provider_type, "REG")][column] * markup
            if table[key][column] < floor:
                shortfalls.append((key, column, floor - table[key][column]))
    assert len(shortfalls) == 6
    assert all(gap < CENT for _, _, gap in shortfalls)


@pytest.mark.parametrize("year", YEARS)
def test_star_levels_two_points_apart(year):
    table = TABLES[year]
    failures = []
    for key in _regulated(table):
        region, provider_type, rating = key
        if rating != "REG":
            continue
        for column in COLUMNS:
            tiers = [
                table[(region, provider_type, r)][column]
                for r in ("TRS2", "TRS3", "TRS4")
            ]
            if any(
                higher - lower < STAR_GAP * table[key][column]
                for lower, higher in zip(tiers, tiers[1:])
            ):
                failures.append((key, column, tiers))
    _assert_none(failures)


@pytest.mark.parametrize("year", YEARS)
def test_school_ready_rates_equal_two_star_rates(year):
    table = TABLES[year]
    _assert_none(
        [
            (key, column)
            for key in _regulated(table)
            if key[2] == "TSR"
            for column in COLUMNS
            if table[key][column] != table[(key[0], key[1], "TRS2")][column]
        ]
    )


@pytest.mark.parametrize("year", YEARS)
def test_blended_rates_follow_the_formula(year):
    failures = []
    for key, row in TABLES[year].items():
        for age in BLENDED_AGES:
            full_time = row[f"age_{age}_ft"]
            part_time = row[f"age_{age}_pt"]
            expected = _half_up((175 * part_time + 30 * full_time) / Decimal(205))
            if row[f"age_{age}_bt"] != expected:
                failures.append((key, age, row[f"age_{age}_bt"], expected))
    _assert_none(failures)


@pytest.mark.parametrize("year", YEARS)
def test_part_time_and_blended_rates_within_full_time(year):
    # Not a rule, but true of both tables: a part-time rate above the full-time
    # rate means a value landed in the wrong column.
    failures = []
    for key, row in TABLES[year].items():
        for age in AGES:
            if row[f"age_{age}_pt"] > row[f"age_{age}_ft"]:
                failures.append((key, age))
        for age in BLENDED_AGES:
            if not (
                row[f"age_{age}_pt"] <= row[f"age_{age}_bt"] <= row[f"age_{age}_ft"]
            ):
                failures.append((key, age))
    _assert_none(failures)


def test_bcy_2026_rates_keep_bcy_2025_levels():
    _assert_none(
        [
            (key, column, TABLES[2025][key][column], TABLES[2026][key][column])
            for key in _regulated(TABLES[2025])
            for column in COLUMNS
            if TABLES[2026][key][column] < TABLES[2025][key][column]
        ]
    )


def test_four_age_rates_equal_the_lowest_eight_age_rate_in_each_group():
    groups = sorted(set(FOUR_AGE_GROUP.values()))
    failures = []
    checked = 0
    for key in _regulated(TABLES[2025]):
        region, provider_type, rating = key
        for group in groups:
            ages = [age for age, name in FOUR_AGE_GROUP.items() if name == group]
            for suffix in ("ft", "pt"):
                schedule = SCHEDULE[suffix]
                cell = (region, provider_type, rating, group, schedule)
                four_age = _four_age_rate(*cell)
                if four_age == UNCORRECTED_FOUR_AGE.get(cell):
                    continue
                checked += 1
                lowest = min(TABLES[2025][key][f"age_{age}_{suffix}"] for age in ages)
                if four_age != lowest:
                    failures.append((cell, four_age, lowest))
    assert checked >= 3_360 - len(UNCORRECTED_FOUR_AGE)
    _assert_none(failures)


def test_school_age_blended_rates_equal_the_four_age_table():
    table = TABLES[2025]
    failures = []
    for key, row in table.items():
        region, provider_type, rating = key
        rating = "NONE" if provider_type == "RELATIVE" else rating
        printed = _four_age_rate(region, provider_type, rating, "SCHOOL_AGE", "BLENDED")
        if row["age_6_13yr_bt"] != printed:
            failures.append((key, row["age_6_13yr_bt"], printed))
    _assert_none(failures)


def test_relative_rows_carry_the_four_age_table_rates():
    failures = []
    for key, row in TABLES[2025].items():
        region, provider_type, _ = key
        if provider_type != "RELATIVE":
            continue
        for age, group in FOUR_AGE_GROUP.items():
            for suffix in ("ft", "pt"):
                printed = _four_age_rate(
                    region, "RELATIVE", "NONE", group, SCHEDULE[suffix]
                )
                if row[f"age_{age}_{suffix}"] != printed:
                    failures.append((region, age, suffix, printed))
    _assert_none(failures)


def test_relative_rates_change_only_where_twc_changed_them():
    changes = {
        (key[0], column): (TABLES[2025][key][column], TABLES[2026][key][column])
        for key in TABLES[2025]
        if key[1] == "RELATIVE"
        for column in COLUMNS
        if TABLES[2025][key][column] != TABLES[2026][key][column]
    }
    assert changes == RELATIVE_CHANGES_IN_BCY_2026


AGE_GROUP_COLUMN = {
    "AGE_0_11_MONTHS": "0_11m",
    "AGE_12_17_MONTHS": "12_17m",
    "AGE_18_23_MONTHS": "18_23m",
    "AGE_2_YEARS": "2yr",
    "AGE_3_YEARS": "3yr",
    "AGE_4_YEARS": "4yr",
    "AGE_5_YEARS": "5yr",
    "AGE_6_13_YEARS": "6_13yr",
}
SCHEDULE_SUFFIX = {"FULL_TIME": "ft", "PART_TIME": "pt", "BLENDED": "bt"}


def _table_rate(year, region, provider_type, rating, age_group, schedule):
    # Reads the CSV directly, as an independent path to what the lookup returns.
    # The tables print no blended rate below age 4, so those requests get nothing.
    row = TABLES[year].get((region, provider_type, rating))
    column = f"age_{AGE_GROUP_COLUMN[age_group]}_{SCHEDULE_SUFFIX[schedule]}"
    if row is None or column not in row:
        return 0.0
    return float(row[column])


@pytest.fixture(scope="module")
def model():
    from policyengine_us.parameters.gov.states.tx.twc.ccs.payment.rates_expanded_age_groups import (
        get_rates,
    )
    from policyengine_us.variables.gov.states.tx.twc.ccs.payment.tx_ccs_care_schedule import (
        TXCCSCareSchedule,
    )
    from policyengine_us.variables.gov.states.tx.twc.ccs.payment.tx_ccs_payment_rate import (
        _lookup_expanded_rate,
    )
    from policyengine_us.variables.gov.states.tx.twc.ccs.payment.tx_ccs_provider_rating import (
        TXCCSProviderRating,
    )
    from policyengine_us.variables.gov.states.tx.twc.ccs.payment.tx_ccs_provider_type import (
        TXCCSProviderType,
    )
    from policyengine_us.variables.gov.states.tx.twc.ccs.tx_ccs_child_age_category import (
        TexasCCSChildAgeCategory,
    )
    from policyengine_us.variables.gov.states.tx.twc.ccs.tx_ccs_workforce_board_region import (
        TXCCSWorkforceBoardRegion,
    )

    return dict(
        get_rates=get_rates,
        lookup=_lookup_expanded_rate,
        region=TXCCSWorkforceBoardRegion,
        provider_type=TXCCSProviderType,
        rating=TXCCSProviderRating,
        age_group=TexasCCSChildAgeCategory,
        schedule=TXCCSCareSchedule,
    )


REGIONS = sorted({key[0] for key in TABLES[2026]})
PROVIDER_TYPES = ["LCCC", "LCCH", "RCCH", "RELATIVE"]
RATINGS = ["REG", "TRS2", "TRS3", "TRS4", "TSR", "NONE"]


def test_every_table_key_is_a_model_enum_member(model):
    assert {key[0] for table in TABLES.values() for key in table} <= {
        item.name for item in model["region"]
    }
    assert set(PROVIDER_TYPES) == {item.name for item in model["provider_type"]}
    assert set(RATINGS) == {item.name for item in model["rating"]}
    assert set(AGE_GROUP_COLUMN) <= {item.name for item in model["age_group"]}
    assert set(SCHEDULE_SUFFIX) == {item.name for item in model["schedule"]}


@pytest.mark.parametrize("year", YEARS)
def test_get_rates_reads_every_cell(model, year):
    long = model["get_rates"](year)
    assert len(long) == 8_512
    failures = [
        tuple(row)
        for row in long.itertuples(index=False)
        if row.rate
        != _table_rate(
            year,
            row.region,
            row.provider_type,
            row.provider_rating,
            row.age_group,
            row.schedule,
        )
    ]
    _assert_none(failures)


@settings(max_examples=100, deadline=None)
@given(
    year=st.sampled_from(YEARS),
    keys=st.lists(
        st.tuples(
            st.sampled_from(REGIONS),
            st.sampled_from(PROVIDER_TYPES),
            st.sampled_from(RATINGS),
            st.sampled_from(sorted(AGE_GROUP_COLUMN)),
            st.sampled_from(sorted(SCHEDULE_SUFFIX)),
        ),
        min_size=1,
        max_size=30,
    ),
)
def test_lookup_returns_each_cell_in_order_or_zero(model, year, keys):
    # A mixed batch checks that the merge keeps each person's row, and that a
    # combination the table does not print pays nothing.
    regions, provider_types, ratings, age_groups, schedules = map(np.array, zip(*keys))
    result = model["lookup"](
        year,
        model["region"].encode(regions),
        model["provider_type"].encode(provider_types),
        ratings,
        model["age_group"].encode(age_groups),
        model["schedule"].encode(schedules),
    )
    assert result.tolist() == [_table_rate(year, *key) for key in keys]
