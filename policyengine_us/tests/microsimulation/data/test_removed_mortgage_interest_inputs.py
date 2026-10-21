"""
Datasets built before issue #9275's stage 3 can still carry the removed
tax-unit ``first_home_mortgage_interest`` / ``second_home_mortgage_interest``
columns. Loading one must name the ignored columns (policyengine-core's
unknown-column warning) and compute mortgage interest from the person-level
``home_mortgage_interest`` input alone.
"""

import logging

import pandas as pd

from policyengine_us import Microsimulation
from policyengine_us.data.dataset_schema import USSingleYearDataset


def _dataset_with_removed_columns() -> USSingleYearDataset:
    return USSingleYearDataset(
        person=pd.DataFrame(
            {
                "person_id": [1, 2],
                "age": [40.0, 40.0],
                "employment_income": [50_000.0, 0.0],
                "person_household_id": [1, 1],
                "person_tax_unit_id": [1, 1],
                "person_spm_unit_id": [1, 1],
                "person_family_id": [1, 1],
                "person_marital_unit_id": [1, 1],
                "home_mortgage_interest": [900.0, 100.0],
            }
        ),
        household=pd.DataFrame(
            {"household_id": [1], "household_weight": [1.0], "state_fips": [6]}
        ),
        tax_unit=pd.DataFrame(
            {
                "tax_unit_id": [1],
                # Deliberately different from the person-level total so the
                # test proves the removed columns are ignored.
                "first_home_mortgage_interest": [5_000.0],
                "second_home_mortgage_interest": [2_000.0],
            }
        ),
        spm_unit=pd.DataFrame({"spm_unit_id": [1]}),
        family=pd.DataFrame({"family_id": [1]}),
        marital_unit=pd.DataFrame({"marital_unit_id": [1]}),
        time_period=2024,
    )


def test_removed_mortgage_interest_columns_warn_and_are_ignored(caplog):
    with caplog.at_level(logging.WARNING):
        sim = Microsimulation(dataset=_dataset_with_removed_columns())
        interest = sim.calculate("home_mortgage_interest_tax_unit", 2024)

    warnings = [
        record.getMessage()
        for record in caplog.records
        if "do not match any variable" in record.getMessage()
    ]
    assert len(warnings) == 1
    assert "first_home_mortgage_interest" in warnings[0]
    assert "second_home_mortgage_interest" in warnings[0]
    assert interest.values.tolist() == [1_000.0]
