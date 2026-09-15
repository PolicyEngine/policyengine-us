"""CPUC income rules exclude housing subsidies, irrespective of SPM settings.

Explicit SPM configuration and provenance comparisons require the Python API;
the ordinary policy outcomes are also covered by CPUC YAML integration cases.
"""

from copy import deepcopy

import numpy as np
import pytest

from policyengine_us import Simulation


@pytest.mark.parametrize("assisted", [False, True])
def test_assisted_care_income_is_independent_of_spm_selection(assisted):
    year = 2024
    situation = {
        "people": {
            "person1": {
                "age": {year: 40},
                "employment_income": {year: 40_700},
                "pre_subsidy_rent": {year: 36_000},
            }
        },
        "spm_units": {
            "unit": {
                "members": ["person1"],
                "spm_unit_tenure_type": {year: "RENTER"},
                "receives_housing_assistance": {year: assisted},
                "takes_up_housing_assistance_if_eligible": {year: assisted},
                "pre_subsidy_electricity_expense": {year: 1_200},
            }
        },
        "households": {
            "household": {
                "members": ["person1"],
                "state_code": {year: "CA"},
                "pha_payment_standard": {year: 36_000},
            }
        },
    }
    outputs = [
        "ca_cpuc_countable_income",
        "ca_care_income_eligible",
        "ca_care_eligible",
        "ca_care",
        "ca_fera_eligible",
        "ca_fera",
    ]
    results = []
    for spm, county in [
        (None, None),
        ({"geography_kind": "national"}, None),
        ({"geography_kind": "county"}, "06037"),
    ]:
        inputs = deepcopy(situation)
        if county is not None:
            inputs["households"]["household"]["county_fips"] = {year: county}
        simulation = Simulation(situation=inputs, spm=spm)
        assistance = simulation.calculate("housing_assistance", year)[0]
        assert bool(assistance > 0) is assisted
        results.append([simulation.calculate(name, year)[0] for name in outputs])
        assert simulation.spm_provenance()["years"] == {}

    # D.14-08-030 excludes housing subsidies from CARE income. The modeled
    # 2024 CARE limit is $40,880 and the discount is 32.5% of $1,200.
    for result in results:
        np.testing.assert_array_equal(result, [40_700, True, True, 390, False, 0])


def test_cpuc_housing_exclusion_effective_date():
    parameters = Simulation.default_tax_benefit_system_instance.parameters
    before = parameters("2014-08-13").gov.states.ca.cpuc.income_sources
    after = parameters("2014-08-14").gov.states.ca.cpuc.income_sources
    assert "housing_assistance" in before
    assert list(after) == [name for name in before if name != "housing_assistance"]
    assert list(parameters("2026-01-01").gov.states.ca.cpuc.income_sources) == list(
        after
    )
