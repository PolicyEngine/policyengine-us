"""Conserve program awards while allocating housing resources for the SPM."""

from copy import deepcopy

import numpy as np
import pytest

from policyengine_us import Simulation
from policyengine_core.periods import period
from policyengine_core.reforms import Reform
from spm_calculator.errors import SPMInputError


YEAR = 2025


def split_households():
    # Unequal unit sizes, interleaved people, and an independent household
    # distinguish member-share allocation from duplication or array alignment.
    return {
        "people": {name: {"age": {YEAR: 40}} for name in ("a", "b", "c", "d", "e")},
        "spm_units": {
            "head_family": {
                "members": ["a"],
                "housing_assistance": {YEAR: 12_000},
                "hud_ttp": {YEAR: 0},
                "spm_unit_tenure_type": {YEAR: "RENTER"},
            },
            "other_household": {
                "members": ["b", "d"],
                "housing_assistance": {YEAR: 6_000},
                "hud_ttp": {YEAR: 0},
                "spm_unit_tenure_type": {YEAR: "RENTER"},
            },
            "co_residents": {
                "members": ["c", "e"],
                "housing_assistance": {YEAR: 0},
                "hud_ttp": {YEAR: 0},
                "spm_unit_tenure_type": {YEAR: "RENTER"},
            },
        },
        "households": {
            "shared_home": {"members": ["a", "c", "e"]},
            "separate_home": {"members": ["b", "d"]},
        },
    }


def test_subsidy_allocation_conserves_each_households_actual_awards():
    sim = Simulation(situation=split_households())
    np.testing.assert_array_equal(
        sim.calculate("spm_unit_allocated_housing_subsidy", YEAR),
        [4_000, 6_000, 8_000],
    )
    np.testing.assert_array_equal(
        sim.calculate("housing_assistance", YEAR), [12_000, 6_000, 0]
    )
    np.testing.assert_array_equal(
        sim.calculate("spm_unit_allocated_housing_subsidy", YEAR, map_to="household"),
        [12_000, 6_000],
    )
    # Allocation uses no threshold or geography and records no SPM calculation.
    assert sim.spm_provenance()["years"] == {}


def test_multiple_actual_awards_are_preserved_before_spm_allocation():
    situation = split_households()
    situation["spm_units"]["co_residents"]["housing_assistance"] = {YEAR: 3_000}
    sim = Simulation(situation=situation)
    np.testing.assert_array_equal(
        sim.calculate("spm_unit_allocated_housing_subsidy", YEAR),
        [5_000, 6_000, 10_000],
    )
    np.testing.assert_array_equal(
        sim.calculate("housing_assistance", YEAR), [12_000, 6_000, 3_000]
    )


def test_allocated_subsidy_reaches_nonrecipient_spm_unit_before_its_cap():
    sim = Simulation(situation=split_households(), spm={"geography_kind": "national"})
    np.testing.assert_array_equal(
        sim.calculate("spm_unit_capped_housing_subsidy", YEAR),
        [4_000, 6_000, 8_000],
    )


@pytest.mark.parametrize("amount", [0, 1, 12_345.67])
def test_single_unit_allocation_preserves_program_amount(amount):
    sim = Simulation(
        situation={
            "people": {"a": {"age": {YEAR: 40}}},
            "spm_units": {
                "unit": {
                    "members": ["a"],
                    "housing_assistance": {YEAR: amount},
                }
            },
        }
    )
    np.testing.assert_array_equal(
        sim.calculate("spm_unit_allocated_housing_subsidy", YEAR),
        sim.calculate("housing_assistance", YEAR),
    )


def test_zero_awards_need_no_spm_geography():
    situation = deepcopy(split_households())
    for unit in situation["spm_units"].values():
        unit["housing_assistance"] = {YEAR: 0}
    sim = Simulation(situation=situation)
    np.testing.assert_array_equal(
        sim.calculate("spm_unit_capped_housing_subsidy", YEAR), [0, 0, 0]
    )
    assert sim.spm_provenance()["years"] == {}
    np.testing.assert_array_equal(
        sim.calculate("spm_unit_allocated_tenant_payment", YEAR), [0, 0, 0]
    )


@pytest.mark.parametrize("nonrecipient_ttp", [25, 45_000])
def test_only_awarded_families_contribute_tenant_payment(nonrecipient_ttp):
    situation = split_households()
    units = situation["spm_units"]
    units["head_family"]["hud_ttp"] = {YEAR: 3_600}
    units["other_household"]["hud_ttp"] = {YEAR: 900}
    units["co_residents"]["hud_ttp"] = {YEAR: nonrecipient_ttp}
    sim = Simulation(situation=situation, spm={"geography_kind": "national"})
    np.testing.assert_array_equal(
        sim.calculate("spm_unit_allocated_tenant_payment", YEAR), [1_200, 900, 2_400]
    )
    np.testing.assert_array_equal(
        sim.calculate("spm_unit_allocated_tenant_payment", YEAR, map_to="household"),
        [3_600, 900],
    )
    # Even the high counterfactual liability must leave a positive resource
    # for the co-resident unit that receives part of the household subsidy.
    assert sim.calculate("spm_unit_capped_housing_subsidy", YEAR)[2] > 0


def test_independent_unit_caps_do_not_redistribute_unused_housing_value():
    situation = split_households()
    situation["spm_units"]["head_family"]["hud_ttp"] = {YEAR: 90_000}
    sim = Simulation(situation=situation, spm={"geography_kind": "national"})
    np.testing.assert_array_equal(
        sim.calculate("spm_unit_allocated_tenant_payment", YEAR), [30_000, 0, 60_000]
    )
    np.testing.assert_array_equal(
        sim.calculate("spm_unit_capped_housing_subsidy", YEAR), [0, 6_000, 0]
    )
    np.testing.assert_array_equal(
        sim.calculate("housing_assistance", YEAR), [12_000, 6_000, 0]
    )


def real_hud_household(lodger_income=0, lodger_receipt=False):
    return {
        "people": {
            "head": {
                "age": {YEAR: 40},
                "is_household_head": {YEAR: True},
                "employment_income": {YEAR: 12_000},
                "pre_subsidy_rent": {YEAR: 36_000},
            },
            "lodger": {
                "age": {YEAR: 30},
                "employment_income": {YEAR: lodger_income},
            },
            "co_resident": {"age": {YEAR: 25}},
        },
        "spm_units": {
            "head_family": {
                "members": ["head"],
                "receives_housing_assistance": {YEAR: True},
                "takes_up_housing_assistance_if_eligible": {YEAR: True},
                "spm_unit_tenure_type": {YEAR: "RENTER"},
            },
            "lodger_family": {
                "members": ["lodger", "co_resident"],
                "receives_housing_assistance": {YEAR: lodger_receipt},
                "takes_up_housing_assistance_if_eligible": {YEAR: lodger_receipt},
                "spm_unit_tenure_type": {YEAR: "RENTER"},
            },
        },
        "households": {
            "shared_home": {
                "members": ["head", "lodger", "co_resident"],
                "state_code": {YEAR: "CA"},
                "county_fips": {YEAR: "06037"},
                "bedrooms": {YEAR: 2},
                "tenant_pays_utilities": {YEAR: True},
                "tenure_type": {YEAR: "RENTED"},
            }
        },
        "tax_units": {
            name: {"members": [name]} for name in ("head", "lodger", "co_resident")
        },
        "families": {
            name: {"members": [name]} for name in ("head", "lodger", "co_resident")
        },
        "marital_units": {
            name: {"members": [name]} for name in ("head", "lodger", "co_resident")
        },
    }


@pytest.mark.parametrize(
    "lodger_income,lodger_receipt", [(0, False), (150_000, False), (150_000, True)]
)
def test_actual_hud_award_ignores_nonawarded_units_hypothetical_payment(
    lodger_income, lodger_receipt
):
    sim = Simulation(situation=real_hud_household(lodger_income, lodger_receipt))
    np.testing.assert_allclose(
        sim.calculate("housing_assistance", YEAR), [28_392, 0], atol=0.01
    )
    np.testing.assert_allclose(
        sim.calculate("spm_unit_allocated_housing_subsidy", YEAR),
        [9_464, 18_928],
        atol=0.01,
    )
    np.testing.assert_allclose(
        sim.calculate("spm_unit_allocated_tenant_payment", YEAR),
        [1_200, 2_400],
        atol=0.01,
    )
    capped = sim.calculate("spm_unit_capped_housing_subsidy", YEAR)
    assert (capped > 0).all()
    assert (
        sim.calculate("spm_unit_capped_housing_subsidy", YEAR, map_to="household")[0]
        <= 28_392
    )


def test_multiple_actual_awards_conserve_subsidy_and_contributions():
    sim = Simulation(situation=real_hud_household(lodger_receipt=True))
    np.testing.assert_allclose(
        sim.calculate("housing_assistance", YEAR), [28_392, 2_639], atol=0.01
    )
    for name, expected in [
        ("spm_unit_allocated_housing_subsidy", 31_031),
        ("spm_unit_allocated_tenant_payment", 3_625),
    ]:
        np.testing.assert_allclose(
            sim.calculate(name, YEAR, map_to="household"), [expected], atol=0.01
        )


def test_spm_selection_changes_measurement_without_changing_general_benefits():
    outputs = []
    for selection in ({"geography_kind": "county"}, {"geography_kind": "national"}):
        sim = Simulation(situation=real_hud_household(), spm=selection)
        outputs.append(
            {
                name: sim.calculate(name, YEAR)
                for name in (
                    "housing_assistance",
                    "household_benefits",
                    "spm_unit_capped_housing_subsidy",
                )
            }
        )
    for name in ("housing_assistance", "household_benefits"):
        np.testing.assert_array_equal(outputs[0][name], outputs[1][name])
    assert not np.array_equal(
        outputs[0]["spm_unit_capped_housing_subsidy"],
        outputs[1]["spm_unit_capped_housing_subsidy"],
    )


def test_hud_abolition_zeroes_allocations_and_needs_no_measurement():
    def abolish(parameters):
        parameters.gov.hud.abolition.update(period=period(YEAR), value=True)
        return parameters

    class AbolishHUD(Reform):
        def apply(self):
            self.modify_parameters(abolish)

    sim = Simulation(situation=real_hud_household(), reform=AbolishHUD)
    for name in (
        "housing_assistance",
        "spm_unit_allocated_housing_subsidy",
        "spm_unit_allocated_tenant_payment",
        "spm_unit_capped_housing_subsidy",
    ):
        np.testing.assert_array_equal(sim.calculate(name, YEAR), [0, 0])
    assert sim.spm_provenance()["years"] == {}


def test_allocated_unit_with_no_classified_adult_raises_composition_error():
    situation = real_hud_household()
    for name in ("lodger", "co_resident"):
        situation["people"][name]["age"] = {YEAR: 10}
    sim = Simulation(situation=situation)
    with pytest.raises(SPMInputError, match="no classified adult"):
        sim.calculate("spm_unit_capped_housing_subsidy", YEAR)
