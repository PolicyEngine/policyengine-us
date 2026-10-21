"""Check Vermont's renter credit income limit tables against HUD's limits.

32 V.S.A. § 6061(19)-(20) define the full and partial credit limits from HUD's
Section 8 income limits: the extremely low-income limit, and 1.3 times the very
low-income limit. Franklin and Grand Isle use the state average instead. PE
transcribes the department's published tables, and PE also bundles HUD's limits
(gov/hud/income_limits) for FY2024 onward, so the two must agree for every year
both cover. The department rounds to the nearest $10, half up; for Franklin and
Grand Isle it averages across Vermont's twelve HUD areas and rounds that average
to $10 before applying the multiplier. Transcription slips in the 2024 and 2025
tables (including the TY2025 booklet's $88,880 for Washington County, seven
people, where 1.3 x $68,450 gives $88,990) broke this check.
"""

from decimal import ROUND_HALF_UP, Decimal

import pytest

from policyengine_us.parameters.gov.hud.income_limits import income_limits
from policyengine_us.system import system

TABLES = system.parameters.gov.states.vt.tax.income.credits.renter.income_limit_ami
SIZES = range(1, 9)
VERY_LOW_INCOME_MULTIPLIER = Decimal("1.3")
COUNTY_FIPS = {
    "ADDISON_COUNTY_VT": "50001",
    "BENNINGTON_COUNTY_VT": "50003",
    "CALEDONIA_COUNTY_VT": "50005",
    "CHITTENDEN_COUNTY_VT": "50007",
    "ESSEX_COUNTY_VT": "50009",
    "FRANKLIN_COUNTY_VT": "50011",
    "GRAND_ISLE_COUNTY_VT": "50013",
    "LAMOILLE_COUNTY_VT": "50015",
    "ORANGE_COUNTY_VT": "50017",
    "ORLEANS_COUNTY_VT": "50019",
    "RUTLAND_COUNTY_VT": "50021",
    "WASHINGTON_COUNTY_VT": "50023",
    "WINDHAM_COUNTY_VT": "50025",
    "WINDSOR_COUNTY_VT": "50027",
}
STATE_AVERAGE_COUNTIES = ("FRANKLIN_COUNTY_VT", "GRAND_ISLE_COUNTY_VT")


def _table(name):
    """Map (year, county, size) to each value dated January 1 in a table."""
    values = {}
    for size in SIZES:
        for county, parameter in (
            TABLES.children[name].children[str(size)].children.items()
        ):
            for entry in parameter.values_list:
                year, month_day = int(entry.instant_str[:4]), entry.instant_str[5:]
                assert month_day == "01-01", entry.instant_str
                values[(year, county, size)] = entry.value
    return values


PARTIAL = _table("fifty_percent")
FULL = _table("thirty_percent")
TABLE_YEARS = sorted({year for year, _, _ in PARTIAL})
HUD_YEARS = sorted(set(TABLE_YEARS) & set(income_limits["year"].unique().tolist()))


def _round_to_ten(amount):
    return int((Decimal(amount) / 10).quantize(Decimal(1), rounding=ROUND_HALF_UP) * 10)


def _hud(year):
    rows = income_limits[
        (income_limits["year"] == year)
        & income_limits["county_fips"].isin(COUNTY_FIPS.values())
    ].set_index("county_fips")
    assert len(rows) == len(COUNTY_FIPS)
    return rows


def _expected(year, county, size, column, multiplier):
    rows = _hud(year)
    if county in STATE_AVERAGE_COUNTIES:
        # Franklin and Grand Isle share the Burlington-South Burlington HUD
        # area with Chittenden, so the other twelve counties are the twelve
        # distinct HUD areas.
        for other in STATE_AVERAGE_COUNTIES:
            assert rows.loc[COUNTY_FIPS[other]].equals(
                rows.loc[COUNTY_FIPS["CHITTENDEN_COUNTY_VT"]]
            )
        areas = [COUNTY_FIPS[c] for c in COUNTY_FIPS if c not in STATE_AVERAGE_COUNTIES]
        average = Decimal(int(rows.loc[areas, f"{column}_{size}"].sum())) / len(areas)
        return _round_to_ten(_round_to_ten(average) * multiplier)
    return _round_to_ten(
        Decimal(int(rows.loc[COUNTY_FIPS[county], f"{column}_{size}"])) * multiplier
    )


def test_hud_comparison_covers_2024_onward():
    # The published tables start in 2021; pe-us copies each parameter's first
    # value back to 2015 (tools/parameters.py backdate_parameters).
    assert set(range(2021, 2026)) <= set(TABLE_YEARS)
    assert HUD_YEARS[:2] == [2024, 2025]


@pytest.mark.parametrize("year", HUD_YEARS)
@pytest.mark.parametrize("county", sorted(COUNTY_FIPS))
@pytest.mark.parametrize("size", SIZES)
def test_partial_credit_limit_is_1_3_times_hud_very_low_income_limit(
    size, county, year
):
    assert PARTIAL[(year, county, size)] == _expected(
        year, county, size, "very_low_income", VERY_LOW_INCOME_MULTIPLIER
    )


@pytest.mark.parametrize("year", HUD_YEARS)
@pytest.mark.parametrize("county", sorted(COUNTY_FIPS))
@pytest.mark.parametrize("size", SIZES)
def test_full_credit_limit_is_hud_extremely_low_income_limit(size, county, year):
    assert FULL[(year, county, size)] == _expected(
        year, county, size, "extremely_low_income", Decimal(1)
    )


def test_tables_cover_every_county_size_and_year():
    keys = {
        (year, county, size)
        for year in TABLE_YEARS
        for county in COUNTY_FIPS
        for size in SIZES
    }
    assert set(PARTIAL) == keys
    assert set(FULL) == keys


@pytest.mark.parametrize("year", TABLE_YEARS)
@pytest.mark.parametrize("county", sorted(COUNTY_FIPS))
def test_limits_rise_with_household_size_and_full_stays_below_partial(county, year):
    partial = [PARTIAL[(year, county, size)] for size in SIZES]
    full = [FULL[(year, county, size)] for size in SIZES]
    assert partial == sorted(partial)
    assert full == sorted(full)
    assert all(f < p for f, p in zip(full, partial))
    assert all(value % 10 == 0 for value in partial + full)


@pytest.mark.parametrize("year", TABLE_YEARS)
def test_franklin_and_grand_isle_share_the_state_average(year):
    for table in (PARTIAL, FULL):
        assert [table[(year, "FRANKLIN_COUNTY_VT", size)] for size in SIZES] == [
            table[(year, "GRAND_ISLE_COUNTY_VT", size)] for size in SIZES
        ]
