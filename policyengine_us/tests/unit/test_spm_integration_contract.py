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
        # Los Angeles County has an encoded HUD utility allowance; keep gross
        # rent equal to the rent so the cap comparisons hold as written.
        "tenant_pays_utilities": {YEAR: False},
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


@pytest.mark.parametrize(
    "variable",
    [
        "household_benefits",
        "household_net_income",
        "marginal_tax_rate",
        "cbo_household_means_tested_transfers",
    ],
)
def test_general_income_with_housing_assistance_is_independent_of_spm(variable):
    """Benefit aggregates use the actual HUD payment, not its SPM valuation."""
    situation = household(earnings=24_000)
    results = []
    for config in [None, {"geography_kind": "national"}]:
        simulation = Simulation(situation=situation, spm=config)
        assert simulation.calculate("housing_assistance", YEAR)[0] > 0
        results.append(simulation.calculate(variable, YEAR))
        assert np.all(np.isfinite(results[-1]))
        assert simulation.spm_provenance()["years"] == {}
    np.testing.assert_array_equal(*results)


def test_spm_resources_with_housing_assistance_still_require_geography():
    situation = household(earnings=24_000)
    with pytest.raises(SPMInputError) as error:
        Simulation(situation=situation).calculate("spm_unit_net_income", YEAR)
    assert error.value.code == "SPM_GEOGRAPHY_REQUIRED"
    national = Simulation(situation=situation, spm={"geography_kind": "national"})
    assistance = national.calculate("housing_assistance", YEAR)[0]
    capped = national.calculate("spm_unit_capped_housing_subsidy", YEAR)[0]
    assert 0 < capped < assistance
    assert np.all(np.isfinite(national.calculate("spm_unit_net_income", YEAR)))
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


# --- CPUC CARE/FERA countable income -----------------------------------------
#
# CARE and FERA are utility discounts, not poverty measurement.
# gov.states.ca.cpuc.income_sources used to count
# spm_unit_capped_housing_subsidy, which made the discount depend on the SPM
# geography the request selected. CPUC D.14-08-030 section 6.2 and Ordering
# Paragraph 40(3) exclude housing subsidies from the income definition
# altogether, effective August 14, 2014, so from calendar 2015 the list carries
# no housing entry at any valuation. PG&E's application form still lists
# "housing and military subsidies", but PG&E told the Commission on June 5,
# 2026 that it does not use them in its income analysis and will correct the
# form.


def assisted_la_renter(earnings, *, county=None):
    situation = household(earnings=earnings, county=county)
    situation["spm_units"]["spm_unit"]["pre_subsidy_electricity_expense"] = {
        YEAR: 1_800
    }
    # Pin the categorical route off so income is what decides, and the
    # equal-eligibility assertions below cannot pass for an unrelated reason.
    situation["households"]["household"]["ca_care_categorically_eligible"] = {
        YEAR: False
    }
    return situation


CARE_OUTPUTS = ("ca_cpuc_countable_income", "ca_care_income_eligible", "ca_care")


@pytest.mark.parametrize(
    "earnings,eligible",
    [
        # $0 earnings. The assistance is excluded, so only the household's
        # other income counts, well inside the 2024 one-person CARE limit of
        # 2 x $20,440.
        (0, True),
        # The reported case: a Los Angeles renter earning $40,700 with $23,790
        # of assistance. With the subsidy excluded, $40,700 of countable
        # income sits just inside the $40,880 limit under every geography.
        # Counting the capped subsidy flipped this household out of CARE at
        # $310.88 under county selection and left it in under national.
        (40_700, True),
    ],
)
def test_care_eligibility_is_the_same_under_every_spm_geography(earnings, eligible):
    """An assisted household's utility discount must not move with SPM geography.

    The capped subsidy is a poverty-measurement construct: it nets the
    assistance against the housing portion of the SPM threshold, which is
    geographically adjusted. Counting it made one Los Angeles renter
    CARE-eligible nationally and ineligible under county selection. CPUC
    D.14-08-030 excludes housing subsidies from CARE/FERA income outright, so
    neither valuation reaches the discount now.
    """
    national = Simulation(
        situation=assisted_la_renter(earnings),
        spm={"geography_kind": "national"},
    )
    county = Simulation(
        situation=assisted_la_renter(earnings, county="06037"),
        spm={"geography_kind": "county"},
    )
    unconfigured = Simulation(situation=assisted_la_renter(earnings))

    # Guard the guard: the capped subsidy this parameter used to count still
    # differs between the two selections, so equal CARE outputs below are the
    # income definition's doing and not a quiet loss of geographic adjustment.
    assert (
        national.calculate("spm_unit_capped_housing_subsidy", YEAR)[0]
        != (county.calculate("spm_unit_capped_housing_subsidy", YEAR)[0])
    )

    for variable in CARE_OUTPUTS:
        values = [sim.calculate(variable, YEAR)[0] for sim in (national, county)]
        assert values[0] == values[1], variable
    assert bool(national.calculate("ca_care_eligible", YEAR)[0]) is eligible

    # And the same answer with no SPM configuration and no county at all: this
    # is what raised SPM_GEOGRAPHY_REQUIRED for partners requesting CARE.
    for variable in (*CARE_OUTPUTS, "ca_care_eligible"):
        assert (
            unconfigured.calculate(variable, YEAR)[0]
            == national.calculate(variable, YEAR)[0]
        ), variable
    # Nothing was looked up, so no measurement was received.
    assert unconfigured.spm_provenance()["years"] == {}


def test_cpuc_countable_income_excludes_the_housing_assistance_entirely():
    """Non-vacuity: the subsidy is live, and none of it reaches countable income.

    Equal answers across geographies would also hold if the household simply
    had no assistance, so pin that the assistance exists and is excluded
    rather than merely revalued.
    """
    simulation = Simulation(situation=assisted_la_renter(40_700))
    assistance = simulation.calculate("housing_assistance", YEAR)[0]
    assert assistance > 0
    assert simulation.calculate("ca_cpuc_countable_income", YEAR)[0] == pytest.approx(
        40_700
    )


def income_eligible_la_renter(*, receives, county="06037"):
    """A renter HUD would income-qualify, so the imputation has something to bite.

    Earnings of $35,000 against $24,000 of rent leave this household inside the
    HUD low-income limit for Los Angeles County, so it is eligible for housing
    assistance whatever it reports, and `takes_up_housing_assistance_if_eligible`
    defaults to true.
    """
    situation = household(earnings=35_000, county=county, rent=24_000)
    situation["spm_units"]["spm_unit"]["receives_housing_assistance"] = {YEAR: receives}
    situation["spm_units"]["spm_unit"]["pre_subsidy_electricity_expense"] = {
        YEAR: 1_800
    }
    # Pin the categorical route off so income is what decides.
    situation["households"]["household"]["ca_care_categorically_eligible"] = {
        YEAR: False
    }
    return situation


@pytest.mark.parametrize("spm", [None, {"geography_kind": "national"}])
@pytest.mark.parametrize("county", ["06037", None])
def test_cpuc_countable_income_for_a_non_recipient_needs_no_geography(spm, county):
    """The unreported case computes under every selection, county input or not.

    Without a county the HUD income limits do not resolve, so the household is
    not even modelled as voucher-eligible; with one it is. Either way nothing
    consults SPM geography, so no configuration is required and no measurement
    is received.
    """
    simulation = Simulation(
        situation=income_eligible_la_renter(receives=False, county=county),
        spm=spm,
    )
    assert not simulation.calculate("receives_housing_assistance", YEAR)[0]
    assert simulation.calculate("ca_cpuc_countable_income", YEAR)[0] == pytest.approx(
        35_000
    )
    assert bool(simulation.calculate("ca_care_eligible", YEAR)[0])
    assert simulation.spm_provenance()["years"] == {}


def test_cpuc_excludes_the_housing_assistance_a_household_reports_receiving():
    """Reported receipt is excluded too, so the discount survives the voucher.

    The same household as above, now reporting the voucher: D.14-08-030
    excludes housing subsidies from the income definition whether or not the
    household reports them, so $35,000 of earnings alone decides and the
    household keeps CARE. Counting the subsidy would have taken it out.
    """
    simulation = Simulation(
        situation=income_eligible_la_renter(receives=True),
        spm={"geography_kind": "national"},
    )
    assistance = simulation.calculate("housing_assistance", YEAR)[0]
    assert assistance > 0
    assert simulation.calculate("ca_cpuc_countable_income", YEAR)[0] == pytest.approx(
        35_000
    )
    assert bool(simulation.calculate("ca_care_income_eligible", YEAR)[0])
    assert bool(simulation.calculate("ca_care_eligible", YEAR)[0])
    assert simulation.calculate("ca_care", YEAR)[0] == pytest.approx(0.325 * 1_800)
