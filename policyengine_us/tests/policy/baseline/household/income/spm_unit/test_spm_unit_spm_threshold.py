"""Canonical forecast selection and country-construction contract regressions.

These Python cases exercise configuration, errors, registry timing and clone
receipts, which the YAML input schema cannot express.
"""

import json

import numpy as np
import pandas as pd
import pytest

from policyengine_us import Simulation
from policyengine_us.data.dataset_schema import USSingleYearDataset
from policyengine_us.spm import create_spm_provider
from spm_calculator.errors import SPMInputError
from spm_calculator.release import SPMUnit
from spm_calculator.rolling_forecast import load_forecast


AMOUNTS = {
    "spm_unit_reference_spm_threshold": "reference_threshold",
    "spm_unit_unadjusted_spm_threshold": "unadjusted_threshold",
    "spm_unit_geographic_adjustment": "geographic_factor",
    "spm_unit_spm_threshold": "threshold",
    "spm_unit_spm_threshold_housing_portion": "housing_portion",
}


def household(*, county=None, tenure="RENTER", people=None):
    people = people or {
        "person1": {"age": {2024: 40}},
        "person2": {"age": {2024: 40}},
        "person3": {"age": {2024: 10}},
        "person4": {"age": {2024: 8}},
    }
    members = list(people)
    location = {"members": members, "state_code": {2024: "CA"}}
    if county is not None:
        location["county_fips"] = {2024: county}
    return {
        "people": people,
        "households": {"household": location},
        "spm_units": {
            "spm_unit": {
                "members": members,
                "spm_unit_tenure_type": {2024: tenure},
            }
        },
    }


def canonical(forecast, year, tenure, *, adults=2, children=2, county=None):
    location = (
        forecast.resolve_county(year, county)
        if county is not None
        else {"kind": "national", "area_id": None}
    )
    return forecast.calculate_unit(
        SPMUnit(
            unit_id="test",
            year=year,
            num_adults=adults,
            num_children=children,
            tenure=tenure.lower(),
            geography_kind=location["kind"],
            geography_id=location["area_id"],
        )
    )


@pytest.mark.parametrize(
    "tenure", ["RENTER", "OWNER_WITH_MORTGAGE", "OWNER_WITHOUT_MORTGAGE"]
)
def test_every_amount_uses_canonical_final_value_for_every_supported_year(tenure):
    forecast = load_forecast()
    assert list(forecast.years) == list(range(2022, 2036))
    # Explicit period inputs cover the artifact, including its historical years.
    situation = household(county="06037", tenure=tenure)
    for person in situation["people"].values():
        person["age"] = {
            year: next(iter(person["age"].values())) for year in forecast.years
        }
    situation["households"]["household"]["county_fips"] = {
        year: "06037" for year in forecast.years
    }
    situation["spm_units"]["spm_unit"]["spm_unit_tenure_type"] = {
        year: tenure for year in forecast.years
    }
    simulation = Simulation(situation=situation)
    for year in forecast.years:
        expected = canonical(forecast, year, tenure, county="06037")
        for variable, field in AMOUNTS.items():
            result = simulation.calculate(variable, year)
            assert result[0] == np.asarray(expected[field], dtype=result.dtype)
    assert set(simulation.spm_provenance()["years"]) == {
        str(year) for year in forecast.years
    }


def test_published_national_reference_is_exact_before_storage_cast():
    # 2024 Census/BLS Betson renter amount in the pinned official workbook.
    provider = create_spm_provider({"geography_kind": "national"})
    result = provider.calculate_unit(year=2024, adults=2, children=2, tenure="renter")
    assert result["reference_threshold"] == 39_219.893902


@pytest.mark.parametrize(
    "county,code",
    [
        (None, "SPM_GEOGRAPHY_REQUIRED"),
        ("", "SPM_GEOGRAPHY_REQUIRED"),
        # County FIPS is a string input, so every non-string value reaches the
        # forecast as a string. A CPS within-state code, a FIPS code that lost
        # its leading zero to an integer column and a missing value are absent
        # counties, not unavailable ones.
        (5, "SPM_GEOGRAPHY_REQUIRED"),
        (6037, "SPM_GEOGRAPHY_REQUIRED"),
        ("6037", "SPM_GEOGRAPHY_REQUIRED"),
        (float("nan"), "SPM_GEOGRAPHY_REQUIRED"),
        ("99999", "SPM_GEOGRAPHY_UNAVAILABLE"),
    ],
)
def test_state_only_or_unknown_county_never_selects_national(county, code):
    simulation = Simulation(situation=household(county=county))
    with pytest.raises(SPMInputError) as error:
        simulation.calculate("spm_unit_spm_threshold", 2025)
    assert error.value.to_dict()["code"] == code
    assert simulation.spm_config["geography_kind"] == "county"
    if code == "SPM_GEOGRAPHY_REQUIRED":
        # The message has to name the caller's fix, not the artifact.
        message = str(error.value)
        assert "five-digit string" in message
        assert 'geography_kind="national"' in message


def test_explicit_national_and_serialized_round_trip():
    simulation = Simulation(situation=household(), spm={"geography_kind": "national"})
    config = json.loads(json.dumps(simulation.spm_config))
    assert config["forecast_content_sha256"] == load_forecast().content_sha256
    assert config["scenario"] == load_forecast().default_scenario
    repeated = Simulation(situation=household(), spm=config)
    assert (
        repeated.calculate("spm_unit_spm_threshold", 2025)[0]
        == simulation.calculate("spm_unit_spm_threshold", 2025)[0]
    )
    assert simulation.calculate("spm_unit_geographic_adjustment", 2025)[0] == 1
    config["scenario"] = "unavailable"
    assert simulation.spm_config["scenario"] != "unavailable"


@pytest.mark.parametrize(
    "config",
    [
        {"forecast_content_sha256": "0" * 64},
        {"scenario": "unavailable"},
        {"geography_kind": "state"},
        {"missing_geography": "national"},
        {"year_policy": "pe_cpi_u"},
    ],
)
def test_unavailable_selection_or_consumer_extrapolation_rejected(config):
    with pytest.raises(ValueError):
        create_spm_provider(config)


def test_unknown_year_has_no_country_cpi_extrapolation():
    simulation = Simulation(situation=household(county="06037"))
    with pytest.raises(ValueError, match="no entry"):
        simulation.calculate("spm_unit_spm_threshold", 2099)


@pytest.mark.parametrize(
    "role",
    ["is_household_head", "is_household_spouse", "is_spm_independent_minor_role"],
)
def test_minor_primitive_exists_before_input_parsing_and_does_not_change_benefit_counts(
    role,
):
    simulation = Simulation(
        situation=household(people={"person1": {"age": {2024: 16}, role: True}}),
        spm={"geography_kind": "national"},
    )
    assert simulation.calculate("spm_measurement_adults", 2025)[0] == 1
    assert simulation.calculate("spm_measurement_children", 2025)[0] == 0
    assert simulation.calculate("spm_unit_count_adults", 2025)[0] == 0
    assert simulation.calculate("spm_unit_count_children", 2025)[0] == 1
    assert simulation.calculate("spm_unit_spm_threshold", 2025)[0] > 0


def test_no_adult_requires_explicit_composition_instead_of_minimum_one():
    simulation = Simulation(
        situation=household(people={"person1": {"age": {2024: 16}}}),
        spm={"geography_kind": "national"},
    )
    with pytest.raises(SPMInputError) as error:
        simulation.calculate("spm_unit_spm_threshold", 2025)
    assert error.value.to_dict()["code"] == "SPM_COMPOSITION_REQUIRED"


def test_clone_keeps_cached_calculation_provenance_but_detaches_receipts():
    simulation = Simulation(situation=household(county="06037"))
    expected = simulation.calculate("spm_unit_spm_threshold", 2025)[0]
    clone = simulation.clone()
    assert clone.calculate("spm_unit_spm_threshold", 2025)[0] == expected
    assert clone.spm_provenance()["years"] == simulation.spm_provenance()["years"]
    clone.calculate("spm_unit_spm_threshold", 2026)
    assert "2026" not in simulation.spm_provenance()["years"]
    detached = clone.spm_provenance()
    detached["years"].clear()
    assert clone.spm_provenance()["years"]


def test_policy_reform_baseline_uses_same_explicit_spm_selection():
    simulation = Simulation(
        situation=household(), reform=(), spm={"geography_kind": "national"}
    )
    assert simulation.baseline.spm_config == simulation.spm_config
    assert (
        simulation.baseline.calculate("spm_unit_spm_threshold", 2025)[0]
        == simulation.calculate("spm_unit_spm_threshold", 2025)[0]
    )


def test_dataset_cannot_override_formula_owned_threshold():
    person = pd.DataFrame(
        {
            "person_id": [1],
            "age": [40],
            **{
                f"person_{entity}_id": [1]
                for entity in (
                    "household",
                    "tax_unit",
                    "spm_unit",
                    "family",
                    "marital_unit",
                )
            },
        }
    )
    dataset = USSingleYearDataset(
        person=person,
        household=pd.DataFrame({"household_id": [1], "county_fips": ["06037"]}),
        tax_unit=pd.DataFrame({"tax_unit_id": [1]}),
        spm_unit=pd.DataFrame({"spm_unit_id": [1], "spm_unit_spm_threshold": [1.0]}),
        family=pd.DataFrame({"family_id": [1]}),
        marital_unit=pd.DataFrame({"marital_unit_id": [1]}),
        time_period=2024,
    )
    with pytest.raises(
        ValueError,
        match="Dataset supplies formula-owned SPM output spm_unit_spm_threshold",
    ):
        Simulation(dataset=dataset)
