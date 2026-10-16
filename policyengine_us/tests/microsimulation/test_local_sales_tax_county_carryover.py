"""Sales tax geography must recognize counties carried into dataset years."""

import numpy as np
import pytest
from policyengine_core.periods import period as as_period

from policyengine_us.tests.microsimulation.test_county_branch_reuse import (
    COUNTY_FIPS,
    DATASET_YEAR,
    EXPECTED,
    _simulation,
)
from policyengine_us.tools.local_sales_tax_geography import _supplied_input
from policyengine_us.variables.household.demographic.geographic.county.county_enum import (
    County,
)

MOVED_COUNTIES = [
    "BALTIMORE_COUNTY_MD",
    "QUEENS_COUNTY_NY",
    "SAN_DIEGO_COUNTY_CA",
]


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


def test_calculated_county_shadowing_same_year_input_is_not_supplied():
    simulation = _simulation("county")
    year = DATASET_YEAR + 1
    simulation.set_input("county", year, County.encode(np.array(MOVED_COUNTIES)))
    branch = simulation.get_branch("shadowed")
    # Match the earlier input so only the hidden same-year input rules it out.
    branch.get_holder("county").put_in_cache(
        County.encode(np.array(EXPECTED)), as_period(year), branch.branch_name
    )

    assert (
        _supplied_input(branch.populations["household"], as_period(year), "county")
        is None
    )


def test_calculated_county_shadowing_source_input_is_not_supplied():
    simulation = _simulation("county")
    branch = simulation.get_branch("shadowed")
    # Equal values still cannot give this calculated cache input provenance.
    branch.get_holder("county").put_in_cache(
        County.encode(np.array(EXPECTED)), as_period(DATASET_YEAR), branch.branch_name
    )

    assert (
        _supplied_input(
            branch.populations["household"], as_period(DATASET_YEAR + 1), "county"
        )
        is None
    )


def test_carried_county_differing_from_earlier_input_is_not_supplied():
    simulation = _simulation("county")
    branch = simulation.get_branch("moved")
    branch.set_input(
        "county", DATASET_YEAR + 2, County.encode(np.array(MOVED_COUNTIES))
    )
    # County carries the branch's latest stored value, even into an earlier year.
    # The resolver must compare it with the input preceding the requested year.
    assert (
        _supplied_input(
            branch.populations["household"], as_period(DATASET_YEAR + 1), "county"
        )
        is None
    )
