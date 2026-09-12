"""A reform starting in a future year must have exactly zero impact earlier.

Regression test for https://github.com/PolicyEngine/policyengine-us/issues/9075,
where the reform branch lost uprating on the reformed parameter for the years
between the last legislated value and the reform start, producing spurious
society-wide impacts in pre-start years.
"""

import numpy as np

from policyengine_us.tests.microsimulation.populace_fixture import (
    default_population_sample,
)


def test_future_dated_reform_zero_impact_before_start():
    from policyengine_core.reforms import Reform

    from policyengine_us import Microsimulation

    # The standard deduction is uprated and affects nearly every filer, so a
    # pre-start distortion of the reformed parameter cannot hide in a
    # subsample (unlike a narrow phase-out threshold).
    reform = Reform.from_dict(
        {
            "gov.irs.deductions.standard.amount.SINGLE": {
                "2029-01-01.2100-12-31": 20_000
            }
        },
        country_id="us",
    )

    # A slice of the shipped population, not the legacy policyengine-us-data
    # CPS files: those supply neither source-backed SPM independence roles nor
    # county FIPS codes, so resource outputs fail closed over them. Slicing
    # whole households keeps both simulations on exactly the same population
    # without subsampling two copies of the whole build.
    dataset = default_population_sample()
    baseline = Microsimulation(dataset=dataset)
    reformed = Microsimulation(dataset=dataset, reform=reform)

    # The pre-start year must be the FIRST period calculated on each
    # simulation: computing an earlier period first carries those results
    # forward instead of recomputing from the year's parameters, which masks
    # the reformed parameter. Per-year parameter coverage lives in
    # tests/policy/baseline/parameters/test_future_dated_reform_uprating.py.
    year = 2028
    baseline_net_income = baseline.calc("household_net_income", period=year)
    reformed_net_income = reformed.calc("household_net_income", period=year)
    np.testing.assert_array_equal(
        np.asarray(reformed_net_income),
        np.asarray(baseline_net_income),
        err_msg=(f"Reform starting 2029 changed household net income in {year}"),
    )

    # Guard against a vacuous pass: the same population must show the reform in
    # the first year it starts, or equality above would prove nothing.
    started = np.asarray(reformed.calc("household_net_income", period=2029))
    unreformed = np.asarray(baseline.calc("household_net_income", period=2029))
    assert (started != unreformed).any(), (
        "Reform starting 2029 changed no household net income in 2029"
    )
