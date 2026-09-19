"""Texas care schedules must resolve per person in a dataset simulation."""

import numpy as np
import pandas as pd

from policyengine_us import Microsimulation
from policyengine_us.data.dataset_schema import USSingleYearDataset


def test_tx_ccs_rates_with_unknown_hours_and_mixed_authorizations():
    # One child per household isolates the dataset input and state masking paths.
    ids = np.arange(1, 7)
    person = pd.DataFrame(
        {
            "person_id": ids,
            "person_household_id": ids,
            "person_tax_unit_id": ids,
            "person_spm_unit_id": ids,
            "person_family_id": ids,
            "person_marital_unit_id": ids,
            "age": np.full(6, 3),
            "is_tax_unit_dependent": np.full(6, True),
            "childcare_hours_per_day": [0, 3, 3, 8, 3, 3],
            "childcare_attending_days_per_month": [20, 20, 20, 20, 0, 20],
        }
    )
    household = pd.DataFrame(
        {
            "household_id": ids,
            "household_weight": np.ones(6),
            "state_fips": [48, 48, 48, 48, 48, 6],
            "county_fips": ["48029"] * 5 + ["06037"],
        }
    )
    simulation = Microsimulation(
        dataset=USSingleYearDataset(
            person=person,
            household=household,
            tax_unit=pd.DataFrame({"tax_unit_id": ids}),
            spm_unit=pd.DataFrame({"spm_unit_id": ids}),
            family=pd.DataFrame({"family_id": ids}),
            marital_unit=pd.DataFrame({"marital_unit_id": ids}),
            time_period=2026,
        )
    )
    simulation.set_input(
        "tx_ccs_care_schedule",
        "2026-01",
        [
            "UNSPECIFIED",
            "UNSPECIFIED",
            "FULL_TIME",
            "PART_TIME",
            "UNSPECIFIED",
            "UNSPECIFIED",
        ],
    )

    # BCY26 Alamo LCCC REG age 3: $43 full time, $36.80 part time.
    # Zero billable days and out-of-state children must receive zero payment.
    np.testing.assert_allclose(
        simulation.calculate("tx_ccs_payment_rate", "2026-01"),
        [860, 736, 860, 736, 0, 0],
        atol=0.01,
        rtol=0,
    )
