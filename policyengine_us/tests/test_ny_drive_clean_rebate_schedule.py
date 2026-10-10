"""The NY Drive Clean rebate schedule changes for vehicles purchased after
June 30, 2021.

Section 4 of the NYSERDA Drive Clean Implementation Manual (last updated June
30, 2021) has one table for vehicles purchased on or before June 30, 2021 and
another for vehicles purchased after it, with the MSRP cap for the flat $500
rebate falling from $60,000 to $42,000. The new amounts therefore start on
July 1, 2021. Calendar-year simulations read parameters on January 1;
first-of-month rolling-year YAML tests exercise the formula in June and July.
Core 3.32.15 rejects caching mid-month annual periods, so these parameter tests
cover the exact June 30 boundary and randomized schedule invariants.
Source: https://www.nyserda.ny.gov/-/media/Project/Nyserda/Files/Programs/Drive-Clean-NY/implementation-manual.pdf#page=8
"""

from datetime import date

import numpy as np
import pytest
from hypothesis import example, given
from hypothesis import strategies as st

from policyengine_us.system import system

DRIVE_CLEAN = system.parameters.gov.states.ny.nyserda.drive_clean
ALL_ELECTRIC_RANGES = np.array([10, 20, 39, 40, 100, 120, 199, 200])
# The manual's section 4 tables, at ranges unaffected by the disclosed
# pre-existing 119-mile threshold discrepancy.
OLD_AMOUNTS = [500, 1_100, 1_100, 1_700, 1_700, 2_000, 2_000, 2_000]
NEW_AMOUNTS = [500, 500, 500, 1_000, 1_000, 1_000, 1_000, 2_000]


@pytest.mark.parametrize(
    "instant, amounts, msrp_threshold",
    [
        (
            "2021-06-30",
            OLD_AMOUNTS,
            60_000,
        ),
        (
            "2021-07-01",
            NEW_AMOUNTS,
            42_000,
        ),
    ],
)
def test_drive_clean_schedule_changes_after_june_30_2021(
    instant, amounts, msrp_threshold
):
    scale = DRIVE_CLEAN.amount(instant)

    assert scale.calc(ALL_ELECTRIC_RANGES).tolist() == amounts
    assert DRIVE_CLEAN.flat_rebate.msrp_threshold(instant) == msrp_threshold


@given(st.dates(min_value=date(2017, 3, 21), max_value=date(2022, 12, 31)))
@example(date(2021, 6, 30))
@example(date(2021, 7, 1))
def test_drive_clean_schedule_is_stable_on_each_side_of_transition(calendar_date):
    before_july = calendar_date < date(2021, 7, 1)
    amounts = OLD_AMOUNTS if before_july else NEW_AMOUNTS
    msrp_threshold = 60_000 if before_july else 42_000
    instant = calendar_date.isoformat()

    assert DRIVE_CLEAN.amount(instant).calc(ALL_ELECTRIC_RANGES).tolist() == amounts
    assert DRIVE_CLEAN.flat_rebate.msrp_threshold(instant) == msrp_threshold


@given(st.integers(min_value=2018, max_value=2035))
@example(2021)
@example(2022)
def test_drive_clean_january_first_lookups_retain_calendar_year_schedule(year):
    # All corrected dates lie after January 1, 2021 and before January 1, 2022.
    # Calendar-year lookups therefore retain the same old/new source values.
    instant = f"{year}-01-01"
    amounts = OLD_AMOUNTS if year <= 2021 else NEW_AMOUNTS
    msrp_threshold = 60_000 if year <= 2021 else 42_000

    assert DRIVE_CLEAN.amount(instant).calc(ALL_ELECTRIC_RANGES).tolist() == amounts
    assert DRIVE_CLEAN.flat_rebate.msrp_threshold(instant) == msrp_threshold
