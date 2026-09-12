import pytest

CPS_2023 = "hf://policyengine/policyengine-us-data/cps_2023.h5"
ENHANCED_CPS_2024 = "hf://policyengine/policyengine-us-data/enhanced_cps_2024.h5"


def test_legacy_cps_file_with_stored_measurements_is_rejected_at_load():
    """cps_2023 stores a formula-owned SPM output, so it cannot be loaded.

    The loader rejects saved measurement outputs before any geography selection
    could matter, which is the point of the contract: a population file supplies
    primitive inputs, and observed Census outputs are retained under separate
    report-only names.
    """
    from policyengine_us import Microsimulation

    with pytest.raises(ValueError, match="formula-owned SPM output"):
        Microsimulation(dataset=CPS_2023)


def test_legacy_enhanced_cps_lacks_source_backed_spm_independence_roles():
    """enhanced_cps_2024 loads, but cannot produce SPM measurements.

    Its county column does hold five-digit FIPS codes, so geography is not what
    fails. 18 of its 43,134 SPM units are a lone 15-to-17-year-old carrying no
    source-backed SPM independence role, so those units classify no measurement
    adult, and every output that reaches the threshold - household net income,
    benefits, poverty and marginal tax rates included - fails closed over the
    file. Assert on the threshold itself: it raises straight off the
    composition, without building the whole resource chain over 43,134 units.
    """
    import numpy as np
    from spm_calculator.errors import SPMInputError

    from policyengine_us import Microsimulation

    simulation = Microsimulation(dataset=ENHANCED_CPS_2024)
    counties = np.asarray(simulation.calculate("county_fips", 2024)).astype(str)
    assert np.all(np.char.str_len(counties) == 5)
    assert np.all(np.char.isdigit(counties))

    adults = np.asarray(simulation.calculate("spm_measurement_adults", 2024))
    assert (adults < 1).sum() == 18
    with pytest.raises(SPMInputError) as error:
        simulation.calculate("spm_unit_spm_threshold", 2024)
    assert error.value.code == "SPM_COMPOSITION_REQUIRED"


def test_county_persists_across_periods():
    """Test that county values persist when calculating for different periods.

    When running over a dataset that has county pre-stored, the county formula
    should return the stored value regardless of the period requested, since
    county is a time-invariant geographic variable.

    Uses the NYC dataset, which stores the county enum itself rather than only
    a county FIPS column.
    """
    import numpy as np
    from policyengine_us import Microsimulation

    sim = Microsimulation(
        dataset="hf://policyengine/policyengine-us-data/cities/NYC.h5"
    )
    sim.subsample(100)

    # Verify county is pre-stored in this dataset
    holder = sim.get_holder("county")
    known_periods = holder.get_known_periods()
    assert len(known_periods) > 0, "NYC dataset should have county pre-stored"

    # Get county for a period different from the stored period
    # NYC dataset stores county for 2023, so request 2025
    county_2025 = sim.calculate("county", period=2025).values

    # Get the stored county value for comparison
    stored_period = known_periods[0]
    county_stored = sim.calculate("county", period=stored_period).values

    # Counties should be identical - the 2025 request should return stored value
    assert np.array_equal(county_stored, county_2025), (
        "County values should persist across periods when running over a dataset"
    )

    # Verify we got NYC counties, not Albany (the bug we're fixing)
    from policyengine_us.variables.household.demographic.geographic.county.county_enum import (
        County,
    )

    assert not np.any(county_2025 == County.ALBANY_COUNTY_NY.index), (
        "Should not fall back to Albany county"
    )


def test_default_dataset_loads_and_runs():
    """The no-argument default (certified Populace build) resolves via the
    hf://datasets/ path and entity-level interception, and produces sane
    aggregates.

    This is the only population file the model ships, so it carries the
    society-wide coverage the legacy policyengine-us-data CPS files used to
    provide here: net income across the extended years, in-range income
    deciles, and nonzero earnings.
    """
    import numpy as np
    from policyengine_us import Microsimulation
    from policyengine_us.system import DEFAULT_DATASET

    assert "populace" in DEFAULT_DATASET, (
        "Default dataset should be the certified Populace build."
    )

    sim = Microsimulation()  # no dataset -> DEFAULT_DATASET (hf://datasets/...)
    sim.subsample(1_000)
    for year in (2024, 2025, 2026):
        hnet = sim.calc("household_net_income", period=year)
        assert not hnet.isna().any(), f"NaN household net income in {year}."
    assert sim.calc("adjusted_gross_income", period=2026).sum() > 0, (
        "Total AGI should be positive on the default dataset."
    )
    # Deciles are 1-10, with -1 for negative income.
    for decile_variable in (
        "household_income_decile",
        "spm_unit_income_decile",
        "income_decile",
    ):
        decile = sim.calc(decile_variable)
        assert np.all(decile >= -1) and np.all(decile <= 10), (
            f"{decile_variable} out of bounds."
        )
    for variable in ("employment_income", "self_employment_income"):
        assert sim.calc(variable, period=2024).sum() > 0, f"{variable} is zero in 2024."
