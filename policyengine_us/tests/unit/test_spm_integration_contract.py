"""Cross-package contracts requiring configuration and dtype-aware assertions.

These cases exercise the public Simulation constructor and computed HUD benefits;
the YAML runner cannot express forecast configuration or compare storage casts.
"""

import json

import numpy as np
import pytest

from policyengine_us import Simulation
from spm_calculator.errors import SPMInputError
from spm_calculator.release import SPMUnit
from spm_calculator.rolling_forecast import load_forecast


YEAR = 2024


def household(*, people=None, county=None, earnings=0, rent=36_000):
    if people is None:
        people = {
            "person1": {
                "age": {YEAR: 40},
                "employment_income": {YEAR: earnings},
                "pre_subsidy_rent": {YEAR: rent},
            }
        }
    members = list(people)
    location = {
        "members": members,
        "state_code": {YEAR: "CA"},
        "pha_payment_standard": {YEAR: 36_000},
    }
    if county is not None:
        location["county_fips"] = {YEAR: county}
    return {
        "people": people,
        "households": {"household": location},
        "spm_units": {
            "spm_unit": {
                "members": members,
                "spm_unit_tenure_type": {YEAR: "RENTER"},
                "receives_housing_assistance": {YEAR: True},
            }
        },
    }


@pytest.fixture(scope="module")
def forecast():
    return load_forecast()


def canonical(forecast, *, adults=1, children=0, geography_kind="national", area=None):
    return forecast.calculate_unit(
        SPMUnit(
            unit_id="test",
            year=YEAR,
            num_adults=adults,
            num_children=children,
            tenure="renter",
            geography_kind=geography_kind,
            geography_id=area,
        )
    )


@pytest.mark.parametrize(
    "earnings,rent,limiting_amount",
    [
        (24_000, 36_000, "cap"),
        (24_000, 7_300, "assistance"),
        (40_000, 36_000, "zero"),
    ],
)
def test_housing_cap_uses_computed_hud_benefits(
    forecast, earnings, rent, limiting_amount
):
    simulation = Simulation(
        situation=household(county="06037", earnings=earnings, rent=rent),
        spm={"geography_kind": "national"},
    )
    # Compute actual country formulas from earnings, rent and the PHA standard;
    # neither hud_ttp nor housing_assistance is supplied as a test input.
    tenant_payment = simulation.calculate("hud_ttp", YEAR).astype(np.float64)
    assistance = simulation.calculate("housing_assistance", YEAR).astype(np.float64)
    raw_housing = canonical(forecast)["housing_portion"]
    raw_cap = np.maximum(raw_housing - tenant_payment, 0)
    expected = np.minimum(assistance, raw_cap)
    result = simulation.calculate("spm_unit_capped_housing_subsidy", YEAR)
    np.testing.assert_array_equal(result, expected.astype(result.dtype))
    assert tenant_payment[0] > 0
    assert assistance[0] > 0
    if limiting_amount == "cap":
        assert 0 < raw_cap[0] < assistance[0]
    elif limiting_amount == "assistance":
        assert 0 < assistance[0] < raw_cap[0]
    else:
        assert raw_cap[0] == 0


@pytest.mark.parametrize(
    "earnings,positive_cap",
    [(26_085.168, True), (26_085.17, True), (26_085.172, False)],
)
def test_housing_cap_preserves_raw_amount_at_tenant_payment_boundary(
    forecast, earnings, positive_cap
):
    # Adjacent representable earnings put the computed HUD tenant payment just
    # below, at, and above the stored 2024 national single-renter housing amount.
    simulation = Simulation(
        situation=household(county="06037", earnings=earnings),
        spm={"geography_kind": "national"},
    )
    tenant_payment = simulation.calculate("hud_ttp", YEAR).astype(np.float64)
    assistance = simulation.calculate("housing_assistance", YEAR).astype(np.float64)
    stored_housing = simulation.calculate(
        "spm_unit_spm_threshold_housing_portion", YEAR
    )
    raw_housing = canonical(forecast)["housing_portion"]
    expected = np.minimum(assistance, np.maximum(raw_housing - tenant_payment, 0))
    result = simulation.calculate("spm_unit_capped_housing_subsidy", YEAR)
    np.testing.assert_array_equal(result, expected.astype(result.dtype))
    assert bool(result[0] > 0) is positive_cap
    if positive_cap:
        incorrectly_rounded = np.minimum(
            assistance,
            np.maximum(stored_housing.astype(np.float64) - tenant_payment, 0),
        ).astype(result.dtype)
        assert result[0] != incorrectly_rounded[0]
    if earnings == 26_085.17:
        assert stored_housing[0] == tenant_payment[0]
        assert result[0] > 0


def test_tax_only_state_input_is_lazy_and_spm_never_computes_county(monkeypatch):
    simulation = Simulation(situation=household(earnings=50_000))
    assert simulation.calculate("income_tax", YEAR)[0] > 0
    assert simulation.spm_provenance()["years"] == {}
    # Tax formulas may resolve their own county defaults. SPM must still use
    # only county_fips input, even if an inferred county is already cached.
    original_calculate = simulation.calculate

    def calculate(variable, *args, **kwargs):
        assert variable not in {"county", "first_county_in_state"}
        return original_calculate(variable, *args, **kwargs)

    monkeypatch.setattr(simulation, "calculate", calculate)
    with pytest.raises(SPMInputError) as error:
        simulation.calculate("spm_unit_spm_threshold", YEAR)
    assert error.value.code == "SPM_GEOGRAPHY_REQUIRED"
    assert simulation.calculate("income_tax", YEAR)[0] > 0


@pytest.mark.parametrize("age", [14, 15, 17, 18])
@pytest.mark.parametrize("role", [False, True])
def test_spm_age_boundary_preserves_generic_demographics(age, role):
    simulation = Simulation(
        situation=household(
            people={
                "person1": {
                    "age": {YEAR: age},
                    "is_spm_independent_minor_role": role,
                }
            }
        ),
        spm={"geography_kind": "national"},
    )
    expected_spm_adult = age >= 18 or (age >= 15 and role)
    assert simulation.calculate("spm_measurement_adults", YEAR)[0] == int(
        expected_spm_adult
    )
    assert simulation.calculate("spm_measurement_children", YEAR)[0] == int(
        not expected_spm_adult
    )
    assert bool(simulation.calculate("is_adult", YEAR)[0]) is (age >= 18)
    assert bool(simulation.calculate("is_child", YEAR)[0]) is (age < 18)
    assert simulation.calculate("spm_unit_count_adults", YEAR)[0] == int(age >= 18)
    assert simulation.calculate("spm_unit_count_children", YEAR)[0] == int(age < 18)
    if expected_spm_adult:
        assert simulation.calculate("spm_unit_spm_threshold", YEAR)[0] > 0
    else:
        with pytest.raises(SPMInputError) as error:
            simulation.calculate("spm_unit_spm_threshold", YEAR)
        assert error.value.to_dict()["code"] == "SPM_COMPOSITION_REQUIRED"


def test_household_roles_preserve_native_spm_membership(forecast):
    people = {
        "person1": {"age": {YEAR: 40}},
        "person2": {"age": {YEAR: 15}, "is_household_spouse": True},
        "person3": {"age": {YEAR: 17}, "is_household_head": True},
        "person4": {"age": {YEAR: 14}, "is_household_head": True},
    }
    simulation = Simulation(
        situation=household(people=people), spm={"geography_kind": "national"}
    )
    np.testing.assert_array_equal(
        simulation.calculate("is_spm_independent_minor_role", YEAR),
        [False, True, True, True],
    )
    assert simulation.calculate("spm_unit_size", YEAR)[0] == 4
    assert simulation.calculate("spm_unit_count_adults", YEAR)[0] == 1
    assert simulation.calculate("spm_unit_count_children", YEAR)[0] == 3
    assert simulation.calculate("spm_measurement_adults", YEAR)[0] == 3
    assert simulation.calculate("spm_measurement_children", YEAR)[0] == 1
    threshold = simulation.calculate("spm_unit_spm_threshold", YEAR)
    expected = canonical(forecast, adults=3, children=1)["threshold"]
    assert threshold[0] == np.asarray(expected, dtype=threshold.dtype)


def test_fixed_metro_matches_county_resolution_without_county_input(forecast):
    assignment = forecast.resolve_county(YEAR, "06037")
    assert assignment["kind"] == "metro"
    config = {"geography_kind": "metro", "geography_id": assignment["area_id"]}
    fixed = Simulation(situation=household(), spm=config)
    observed = Simulation(situation=household(county="06037"))
    fixed_threshold = fixed.calculate("spm_unit_spm_threshold", YEAR)
    np.testing.assert_array_equal(
        fixed_threshold, observed.calculate("spm_unit_spm_threshold", YEAR)
    )
    expected = canonical(forecast, geography_kind="metro", area=assignment["area_id"])[
        "threshold"
    ]
    assert fixed_threshold[0] == np.asarray(expected, dtype=fixed_threshold.dtype)
    assert fixed.spm_config["geography_id"] == assignment["area_id"]
    provenance = json.loads(json.dumps(fixed.spm_provenance()))
    assert provenance["geography_kind"] == "metro"
    assert provenance["geographies"][0]["county_assignment"] is None
    assert (
        observed.spm_provenance()["geographies"][0]["county_assignment"]["county_fips"]
        == "06037"
    )


def test_county_location_requires_observed_input_instead_of_fixed_geography_id():
    with pytest.raises(ValueError, match="Only a fixed metro"):
        Simulation(
            situation=household(),
            spm={"geography_kind": "county", "geography_id": "06037"},
        )


@pytest.mark.parametrize("variable", ["household_net_income", "marginal_tax_rate"])
@pytest.mark.parametrize("national", [False, True])
def test_resource_consumers_without_housing_assistance_never_touch_geography(
    variable, national
):
    """A unit with nothing to cap must not need SPM geography or composition.

    Partners request net income, benefits and marginal rates without any SPM
    measurement, and most households carry no housing assistance; the cap
    consults the canonical housing portion only for units that do.
    """
    situation = household(earnings=50_000)
    situation["spm_units"]["spm_unit"]["receives_housing_assistance"] = {YEAR: False}
    simulation = Simulation(
        situation=situation,
        spm={"geography_kind": "national"} if national else None,
    )
    assert simulation.calculate("housing_assistance", YEAR)[0] == 0
    result = simulation.calculate(variable, YEAR)
    assert np.all(np.isfinite(result))
    assert np.all(result > 0)
    assert simulation.calculate("spm_unit_capped_housing_subsidy", YEAR)[0] == 0
    # No measurement was looked up, so nothing was received.
    assert simulation.spm_provenance()["years"] == {}


@pytest.mark.parametrize("variable", ["household_net_income", "marginal_tax_rate"])
def test_resource_consumers_with_housing_assistance_require_geography(variable):
    """Once there is assistance to cap, the county requirement applies.

    Earnings stay low so the tenant payment sits below the housing portion
    and the cap binds on the assistance rather than on zero.
    """
    situation = household(earnings=6_000)
    situation["spm_units"]["spm_unit"]["housing_assistance"] = {YEAR: 5_000}
    with pytest.raises(SPMInputError) as error:
        Simulation(situation=situation).calculate(variable, YEAR)
    assert error.value.code == "SPM_GEOGRAPHY_REQUIRED"
    assert error.value.to_dict()["code"] == "SPM_GEOGRAPHY_REQUIRED"
    national = Simulation(situation=situation, spm={"geography_kind": "national"})
    result = national.calculate(variable, YEAR)
    assert np.all(np.isfinite(result))
    capped = national.calculate("spm_unit_capped_housing_subsidy", YEAR)[0]
    assert 0 < capped <= 5_000
    assert str(YEAR) in national.spm_provenance()["years"]


def two_household_population(*, assisted_county):
    """Household A has housing assistance to cap; household B has none and no county."""
    return {
        "people": {
            "a": {
                "age": {YEAR: 40},
                "employment_income": {YEAR: 6_000},
                "pre_subsidy_rent": {YEAR: 36_000},
            },
            "b": {
                "age": {YEAR: 40},
                "employment_income": {YEAR: 50_000},
                "pre_subsidy_rent": {YEAR: 36_000},
            },
        },
        "households": {
            "household_a": {
                "members": ["a"],
                "state_code": {YEAR: "CA"},
                "pha_payment_standard": {YEAR: 36_000},
                **(
                    {"county_fips": {YEAR: assisted_county}}
                    if assisted_county is not None
                    else {}
                ),
            },
            "household_b": {
                "members": ["b"],
                "state_code": {YEAR: "CA"},
                "pha_payment_standard": {YEAR: 36_000},
            },
        },
        "spm_units": {
            "unit_a": {
                "members": ["a"],
                "spm_unit_tenure_type": {YEAR: "RENTER"},
                "housing_assistance": {YEAR: 5_000},
            },
            "unit_b": {
                "members": ["b"],
                "spm_unit_tenure_type": {YEAR: "RENTER"},
                "receives_housing_assistance": {YEAR: False},
            },
        },
    }


def test_housing_cap_evaluates_only_assisted_units_in_a_mixed_population():
    """Masked rows align: the assisted unit is capped, the other is zero and free.

    Unit B has no county and no assistance, so it must impose no requirement
    on the population while unit A, which has both, is capped normally.
    """
    simulation = Simulation(situation=two_household_population(assisted_county="06037"))
    assert list(simulation.calculate("housing_assistance", YEAR)) == [5_000, 0]
    capped = simulation.calculate("spm_unit_capped_housing_subsidy", YEAR)
    assert capped.dtype == np.float32
    assert 0 < capped[0] <= 5_000
    assert capped[1] == 0
    net_income = simulation.calculate("household_net_income", YEAR)
    assert np.all(np.isfinite(net_income)) and np.all(net_income > 0)
    provenance = simulation.spm_provenance()
    assert str(YEAR) in provenance["years"]
    # Only the assisted unit's county reached the provider: one receipt, for
    # unit A's Los Angeles County, resolved to its metropolitan area.
    assert provenance["geography_kind"] == "county"
    assert len(provenance["geographies"]) == 1
    (receipt,) = provenance["geographies"]
    assert receipt["year"] == YEAR
    assert receipt["tenure"] == "renter"
    assert receipt["geography"]["area_id"] == "31080"


def test_assisted_unit_without_county_fails_closed_in_a_mixed_population():
    """An unassisted neighbour does not relax the requirement for the assisted unit."""
    simulation = Simulation(situation=two_household_population(assisted_county=None))
    with pytest.raises(SPMInputError) as error:
        simulation.calculate("spm_unit_capped_housing_subsidy", YEAR)
    assert error.value.code == "SPM_GEOGRAPHY_REQUIRED"


@pytest.mark.parametrize(
    "state,variable,period,expected",
    [
        # Colorado's need-standard table: zero adults, one child = $117/month.
        ("CO", "co_tanf_need_standard", YEAR, 117 * 12),
        # Minnesota MFIP excludes $100/month of child support for one child.
        ("MN", "mn_mfip_child_support_income_exclusion", "2024-01", 100),
    ],
)
def test_generic_benefit_consumers_do_not_use_spm_measurement_composition(
    state, variable, period, expected
):
    # Each unit has one 16-year-old. The second has a source-backed SPM role;
    # the first has no classified SPM adult. Both still count as benefit children.
    people = {
        name: {
            "age": {YEAR: 16},
            "is_spm_independent_minor_role": role,
            "child_support_received": {YEAR: 1_800},
        }
        for name, role in (("person1", False), ("person2", True))
    }
    simulation = Simulation(
        situation={
            "people": people,
            "spm_units": {name: {"members": [name]} for name in people},
            "households": {
                name: {"members": [name], "state_code": {YEAR: state}}
                for name in people
            },
        }
    )
    np.testing.assert_array_equal(
        simulation.calculate(variable, period), [expected, expected]
    )
    np.testing.assert_array_equal(
        simulation.calculate("spm_unit_count_adults", YEAR), [0, 0]
    )
    np.testing.assert_array_equal(
        simulation.calculate("spm_unit_count_children", YEAR), [1, 1]
    )
    np.testing.assert_array_equal(
        simulation.calculate("spm_measurement_adults", YEAR), [0, 1]
    )
    np.testing.assert_array_equal(
        simulation.calculate("spm_measurement_children", YEAR), [1, 0]
    )
    assert simulation.spm_provenance()["years"] == {}
