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
