import pytest

DATASETS = [
    "hf://policyengine/policyengine-us-data/cps_2023.h5",
    "hf://policyengine/policyengine-us-data/enhanced_cps_2024.h5",
]

YEARS = list(range(2024, 2026))


@pytest.mark.parametrize("dataset", DATASETS)
@pytest.mark.parametrize("year", YEARS)
def test_microsim_runs(dataset: str, year: int):
    import numpy as np
    from policyengine_us import Microsimulation

    sim = Microsimulation(dataset=dataset)
    sim.subsample(1_000)
    hnet = sim.calc("household_net_income", period=year)
    assert not hnet.isna().any(), "Some households have NaN net income."
    # Deciles are 1-10, with -1 for negative income.
    DECILES = [
        "household_income_decile",
        "spm_unit_income_decile",
        "income_decile",
    ]
    for decile_var in DECILES:
        decile = sim.calc(decile_var)
        assert np.all(decile >= -1) and np.all(
            decile <= 10
        ), f"{decile_var} out of bounds."

    # Check that the microsim calculates important variables as nonzero in current year.
    for var in ["employment_income", "self_employment_income"]:
        assert sim.calc(var, period=2024).sum() > 0, f"{var} is zero in 2024."


def test_county_persists_across_periods():
    """Test that county values persist when calculating for different periods.

    When running over a dataset, county should return the stored value
    regardless of the period requested, since it's a time-invariant
    geographic variable.
    """
    import numpy as np
    from policyengine_us import Microsimulation

    sim = Microsimulation(
        dataset="hf://policyengine/policyengine-us-data/cps_2023.h5"
    )
    sim.subsample(100)

    # Get county for base period and a different period
    county_2024 = sim.calculate("county", period=2024).values
    county_2025 = sim.calculate("county", period=2025).values

    # Counties should be identical across periods
    assert np.array_equal(
        county_2024, county_2025
    ), "County values should persist across periods when running over a dataset"
