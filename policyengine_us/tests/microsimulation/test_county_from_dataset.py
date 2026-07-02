"""County must compute from stored county_fips when running over a dataset.

Datasets that carry the ``county_fips`` input (but no stored ``county``)
previously collapsed every household to ``first_county_in_state``, zeroing
county-derived variables like ``in_nyc`` and ``nyc_income_tax`` nationwide
(PolicyEngine/populace#34).
"""

import numpy as np
import pandas as pd

from policyengine_us import Microsimulation
from policyengine_us.data.dataset_schema import USSingleYearDataset

YEAR = 2024


def _dataset_with_county_fips(
    county_fips: list[str], state_fips: list[int] | None = None
) -> USSingleYearDataset:
    n = len(county_fips)
    ids = np.arange(1, n + 1)
    person = pd.DataFrame(
        {
            "person_id": ids,
            "person_household_id": ids,
            "person_tax_unit_id": ids,
            "person_spm_unit_id": ids,
            "person_family_id": ids,
            "person_marital_unit_id": ids,
            "age": np.full(n, 40.0),
            "employment_income": np.full(n, 100_000.0),
        }
    )
    household = pd.DataFrame(
        {
            "household_id": ids,
            "state_fips": np.asarray(
                state_fips
                if state_fips is not None
                else [int(fips[:2]) for fips in county_fips],
                dtype="int64",
            ),
            "county_fips": county_fips,
            "household_weight": np.full(n, 1.0),
        }
    )
    return USSingleYearDataset(
        person=person,
        household=household,
        tax_unit=pd.DataFrame({"tax_unit_id": ids}),
        spm_unit=pd.DataFrame({"spm_unit_id": ids}),
        family=pd.DataFrame({"family_id": ids}),
        marital_unit=pd.DataFrame({"marital_unit_id": ids}),
        time_period=YEAR,
    )


def test_county_over_dataset_maps_stored_county_fips():
    simulation = Microsimulation(dataset=_dataset_with_county_fips(["36047", "06037"]))

    county_str = simulation.calculate("county_str", YEAR)

    assert county_str.tolist() == [
        "KINGS_COUNTY_NY",
        "LOS_ANGELES_COUNTY_CA",
    ]


def test_in_nyc_and_nyc_income_tax_recompute_from_stored_county_fips():
    simulation = Microsimulation(dataset=_dataset_with_county_fips(["36047", "06037"]))

    in_nyc = simulation.calculate("in_nyc", YEAR)
    nyc_income_tax = simulation.calculate("nyc_income_tax", YEAR)

    assert in_nyc.tolist() == [True, False]
    assert nyc_income_tax.values[0] > 0
    assert nyc_income_tax.values[1] == 0


def test_county_over_dataset_without_fips_still_falls_back():
    simulation = Microsimulation(
        dataset=_dataset_with_county_fips(["", ""], state_fips=[36, 6])
    )

    county_str = simulation.calculate("county_str", YEAR)

    # No stored county and no county_fips: the state's first county remains
    # the documented fallback.
    assert county_str.tolist() == [
        "ALBANY_COUNTY_NY",
        "ALAMEDA_COUNTY_CA",
    ]
