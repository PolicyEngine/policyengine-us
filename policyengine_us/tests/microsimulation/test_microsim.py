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
    adult and every output that reaches the threshold fails closed over the
    file. Only the threshold is asserted here: it raises straight off the
    composition, without building the whole resource chain over 43,134 units.

    Resource outputs are no longer among the outputs that reach it. The
    capped housing subsidy asks for the SPM housing portion only for units
    receiving housing assistance, and none of these 18 units does - which is
    asserted below - so household net income and benefits compute over the
    file. Computing them here would add two minutes to this suite, so they
    are left to the resource tests.
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
    assisted = np.asarray(
        simulation.calculate("receives_housing_assistance", 2024, map_to="spm_unit")
    )
    assert assisted.sum() == 870
    assert not assisted[adults < 1].any()
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


def test_default_dataset_allocates_no_housing_share_to_an_unclassified_unit():
    """The member-share housing allocation over the whole certified default build.

    `spm_unit_allocated_housing_subsidy` prorates a household's modeled
    `housing_assistance` to every SPM unit in that household by member share,
    and `spm_unit_capped_housing_subsidy` consults the canonical housing
    portion for every unit holding a positive share. That consultation reaches
    `SPM_COMPOSITION_REQUIRED`, so a co-resident unit that classifies no
    measurement adult - everyone under 15, or 15 to 17 without a source-backed
    independence role - would now fail the whole population's resource chain
    where the shipped 2.0.1 valuation left it at zero.

    This probe is over `populace_us_2024`, the certified default build, at full
    population with no subsample: `test_default_dataset_loads_and_runs`
    subsamples 1,000 units, which cannot rule out a pattern this rare. If the
    count below is ever nonzero, the allocation needs a guard - allocate only
    among units that classify an adult and leave the remainder with the awarded
    unit - and that decision belongs to a reviewer, not to this test.
    """
    import gc

    import numpy as np
    from spm_calculator.errors import SPMInputError

    from policyengine_us import Microsimulation

    simulation = Microsimulation()  # populace_us_2024, full population.
    allocated = np.asarray(
        simulation.calculate("spm_unit_allocated_housing_subsidy", 2024)
    )
    adults = np.asarray(simulation.calculate("spm_measurement_adults", 2024))
    unclassified = int(((allocated > 0) & (adults < 1)).sum())
    assert unclassified == 0, (
        f"populace_us_2024 (certified default build): {unclassified} of "
        f"{allocated.size} SPM units hold an allocated housing share while "
        "classifying no measurement adult, so the member-share allocation "
        "raises SPM_COMPOSITION_REQUIRED over the whole population."
    )

    # The whole-population resource chain does not fit the hosted runner's
    # memory beside the arrays above (the job was killed twice at this point),
    # so the completion check runs on a subsample. The count above is the
    # full-population fact; this only shows the chain still completes.
    del allocated, adults, simulation
    gc.collect()
    sample = Microsimulation()
    sample.subsample(10_000)
    try:
        net_income = np.asarray(sample.calculate("spm_unit_net_income", 2024))
    except SPMInputError as error:
        pytest.fail(
            "populace_us_2024 (certified default build, 10,000-unit subsample): "
            f"the SPM resource chain raised {error.code} even though "
            f"{unclassified} allocated units classify no measurement adult, so "
            f"the housing allocation is not what failed: {error}"
        )
    assert (
        net_income.size
        == np.asarray(sample.calculate("spm_unit_allocated_housing_subsidy", 2024)).size
    ), (
        "populace_us_2024 (certified default build): net income and the "
        "housing allocation must cover the same SPM units."
    )


def test_legacy_enhanced_cps_allocates_no_housing_share_to_an_unclassified_unit():
    """The same allocation probe over `enhanced_cps_2024`.

    That file is already exercised above, and it is the one population file
    known to contain units classifying no measurement adult: 18 lone
    15-to-17-year-olds. None of them receives a housing award, which the test
    above asserts, but an award is no longer what pulls a unit into the cap -
    a member share of a co-resident family's award does. So the overlap is
    reported here as its own count.

    Only the allocation is probed on this file. Its SPM threshold fails closed
    on those 18 units whatever the housing allocation does, so a resource-chain
    assertion here would pin that older defect rather than this one.
    """
    import numpy as np

    from policyengine_us import Microsimulation

    simulation = Microsimulation(dataset=ENHANCED_CPS_2024)
    allocated = np.asarray(
        simulation.calculate("spm_unit_allocated_housing_subsidy", 2024)
    )
    adults = np.asarray(simulation.calculate("spm_measurement_adults", 2024))
    unclassified = int(((allocated > 0) & (adults < 1)).sum())
    assert unclassified == 0, (
        f"enhanced_cps_2024 (legacy file): {unclassified} of {allocated.size} "
        "SPM units hold an allocated housing share while classifying no "
        "measurement adult."
    )


def test_default_dataset_uses_its_supplied_tax_unit_roles():
    """Every role and filing status on the certified default build is its own.

    `populace_us_2024` ships its tax-unit constructor's roles
    (`tax_unit_role_input`) and filing statuses (`filing_status_input`). Without
    them, age ordering made the oldest adult the head and the next-oldest the
    spouse, pairing adult students with their parents as joint filers, heading
    couples by the older partner rather than the reference person, and leaving
    lone minors with no head. This checks the whole population, person by
    person and unit by unit, in the data year and in an extended year, since
    the loader carries the columns forward rather than the formulas.
    """
    import numpy as np
    import pandas as pd

    from policyengine_us import Microsimulation
    from policyengine_us.system import DEFAULT_DATASET, _resolve_dataset_path

    with pd.HDFStore(_resolve_dataset_path(DEFAULT_DATASET), mode="r") as store:
        person = store["person"][["person_id", "tax_unit_role_input"]]
        tax_unit = store["tax_unit"][["tax_unit_id", "filing_status_input"]]
    roles = person.set_index("person_id")["tax_unit_role_input"].astype(str)
    statuses = tax_unit.set_index("tax_unit_id")["filing_status_input"].astype(str)

    simulation = Microsimulation(dataset_end_year=2026)
    for year in (2024, 2026):
        person_id = np.asarray(simulation.calculate("person_id", year))
        role = roles.reindex(person_id).to_numpy()
        for name, variable in (
            ("HEAD", "is_tax_unit_head"),
            ("SPOUSE", "is_tax_unit_spouse"),
            ("DEPENDENT", "is_tax_unit_dependent"),
        ):
            modelled = np.asarray(simulation.calculate(variable, year)).astype(bool)
            mismatched = int((modelled != (role == name)).sum())
            assert mismatched == 0, (
                f"populace_us_2024 (certified default build), {year}: "
                f"{variable} disagrees with tax_unit_role_input == {name} for "
                f"{mismatched} of {role.size} people."
            )
        tax_unit_id = np.asarray(simulation.calculate("tax_unit_id", year))
        status = statuses.reindex(tax_unit_id).to_numpy()
        modelled = np.asarray(simulation.calculate("filing_status", year)).astype(str)
        mismatched = int((modelled != status).sum())
        assert mismatched == 0, (
            f"populace_us_2024 (certified default build), {year}: "
            f"filing_status disagrees with filing_status_input for "
            f"{mismatched} of {status.size} tax units."
        )
