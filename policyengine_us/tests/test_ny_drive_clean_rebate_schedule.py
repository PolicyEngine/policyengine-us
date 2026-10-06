"""The NY Drive Clean rebate schedule changes for vehicles purchased after
June 30, 2021.

Section 4 of the NYSERDA Drive Clean Implementation Manual (last updated June
30, 2021) has one table for vehicles purchased on or before June 30, 2021 and
another for vehicles purchased after it, with the MSRP cap for the flat $500
rebate falling from $60,000 to $42,000. The new amounts therefore start on
July 1, 2021. Annual simulations read parameters on January 1, so this
schedule is checked at the two instants directly.
"""

import numpy as np
import pytest

from policyengine_us.system import system

DRIVE_CLEAN = system.parameters.gov.states.ny.nyserda.drive_clean
ALL_ELECTRIC_RANGES = np.array([10, 20, 39, 40, 100, 120, 199, 200])


@pytest.mark.parametrize(
    "instant, amounts, msrp_threshold",
    [
        (
            "2021-06-30",
            [500, 1_100, 1_100, 1_700, 1_700, 2_000, 2_000, 2_000],
            60_000,
        ),
        (
            "2021-07-01",
            [500, 500, 500, 1_000, 1_000, 1_000, 1_000, 2_000],
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
