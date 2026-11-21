"""A dataset without its own year stays in the microdata base year.

Core labels such a dataset with the default input period and does not uprate
its values, so following ``CURRENT_YEAR`` would present 2024 dollars as a later
year and leave the base year empty.
"""

import numpy as np
import pandas as pd

from policyengine_us import Microsimulation
from policyengine_us.data.dataset_schema import _DEFAULT_TIME_PERIOD


def test_dataframe_without_years_stays_in_the_base_year():
    wages = [10_000.0, 20_000.0]
    identifiers = [1, 2]
    dataset = pd.DataFrame(
        {
            "person_id": identifiers,
            "household_id": identifiers,
            "tax_unit_id": identifiers,
            "spm_unit_id": identifiers,
            "family_id": identifiers,
            "marital_unit_id": identifiers,
            "age": [40.0, 50.0],
            "employment_income": wages,
            "household_weight": [1.0, 1.0],
        }
    )

    simulation = Microsimulation(dataset=dataset)

    assert int(simulation.dataset.time_period) == _DEFAULT_TIME_PERIOD
    base_year_wages = simulation.calculate("employment_income", _DEFAULT_TIME_PERIOD)
    np.testing.assert_array_equal(np.asarray(base_year_wages), wages)
