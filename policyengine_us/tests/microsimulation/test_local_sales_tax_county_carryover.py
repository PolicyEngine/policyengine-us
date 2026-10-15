"""Sales tax geography must recognize counties carried into dataset years."""

import numpy as np
import pytest
from policyengine_core.periods import period as as_period

from policyengine_us.tests.microsimulation.test_county_branch_reuse import (
    COUNTY_FIPS,
    DATASET_YEAR,
    _simulation,
)


def test_local_sales_tax_uses_county_carried_from_dataset_year():
    # YAML situations do not exercise Microsimulation's dataset carryover.
    simulation = _simulation("county")
    year = DATASET_YEAR + 1
    simulation.set_input(
        "state_sales_tax_income_bracket", year, np.full(len(COUNTY_FIPS), 8)
    )
    simulation.set_input("tax_unit_size", year, np.ones(len(COUNTY_FIPS)))

    assert ("county", simulation.branch_name, as_period(DATASET_YEAR)) in (
        simulation._user_input_keys
    )
    assert simulation.calculate("county", year).iloc[1] == "KINGS_COUNTY_NY"
    assert not any(
        name == "county" and input_period == as_period(year)
        for name, _, input_period in simulation._user_input_keys
    )

    # Kings County uses NYC's 8.875% combined rate and IRS Local Table A.
    assert simulation.calculate("local_sales_tax", year).iloc[1] == pytest.approx(585)
    assert simulation.calculate("combined_sales_tax_rate", year).iloc[
        1
    ] == pytest.approx(0.08875)
    assert simulation.calculate("local_sales_tax_table", year).iloc[1] == "A"
