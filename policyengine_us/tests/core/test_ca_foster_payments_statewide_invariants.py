"""Check every California county and preserve the original LA calculations."""

import numpy as np
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation
from policyengine_us.variables.household.demographic.geographic.county.county_enum import (
    County,
)

YEARS = (2024,)
CA_COUNTIES = tuple(county.name for county in County if county.name.endswith("_CA"))
COUNTIES = (*CA_COUNTIES, "CLARK_COUNTY_NV")
LA_INDEX = COUNTIES.index("LOS_ANGELES_COUNTY_CA")
PAYMENTS = (
    "ca_la_infant_supplement",
    "ca_la_expectant_parent_payment",
)


@st.composite
def foster_parent_cases(draw):
    return {
        "age": draw(st.integers(min_value=14, max_value=23)),
        "children": draw(st.integers(min_value=0, max_value=3)),
        "in_foster_care": draw(st.booleans()),
        "group_home": draw(st.booleans()),
        "pregnancy_month": draw(st.one_of(st.none(), st.integers(0, 10))),
    }


def _boundary_cases():
    def case(**overrides):
        return {
            "age": 20,
            "children": 1,
            "in_foster_care": True,
            "group_home": False,
            "pregnancy_month": 6,
            **overrides,
        }

    return [
        case(pregnancy_month=None),
        case(pregnancy_month=5),
        case(pregnancy_month=6),
        case(pregnancy_month=9),
        case(pregnancy_month=10),
        case(age=21),
        case(in_foster_care=False),
        case(children=0),
        case(group_home=True),
        case(group_home=True, children=3),
        # The original household calculation also counts a parent under 18.
        case(age=17, children=0),
        case(age=17, children=0, in_foster_care=False),
    ]


def _situation(cases):
    people, tax_units, households = {}, {}, {}
    parent_indices = []
    for case_index, case in enumerate(cases):
        for county_index, county in enumerate(COUNTIES):
            suffix = f"{case_index}_{county_index}"
            parent_name = f"parent_{suffix}"
            parent_indices.append(len(people))
            parent = {
                "age": {year: case["age"] for year in YEARS},
                "is_in_foster_care": {
                    f"{year}-01": case["in_foster_care"] for year in YEARS
                },
                "is_in_foster_care_group_home": {
                    f"{year}-01": case["group_home"] for year in YEARS
                },
            }
            if case["pregnancy_month"] is not None:
                parent["current_pregnancy_month"] = {
                    f"{year}-01": case["pregnancy_month"] for year in YEARS
                }
            people[parent_name] = parent
            members = [parent_name]
            for child_index in range(case["children"]):
                child_name = f"child_{suffix}_{child_index}"
                people[child_name] = {"age": {year: 2 for year in YEARS}}
                members.append(child_name)
            tax_units[f"tax_unit_{suffix}"] = {"members": members}
            households[f"household_{suffix}"] = {
                "members": members,
                "state_code": {
                    year: "CA" if county.endswith("_CA") else "NV" for year in YEARS
                },
                "county_str": {year: county for year in YEARS},
            }
    return (
        {"people": people, "tax_units": tax_units, "households": households},
        parent_indices,
    )


def _original_la_amounts(cases):
    """Compute main's LA outcomes without reading the relocated parameters."""
    infant, expectant, foster_eligible, expectant_eligible = [], [], [], []
    for case in cases:
        eligible = case["in_foster_care"] and case["age"] < 21
        pregnancy_month = case["pregnancy_month"] or 0
        pregnant_eligible = eligible and 6 <= pregnancy_month <= 9
        children = case["children"] + (case["age"] < 18)
        infant.append((1_379 if case["group_home"] else 900) * children * eligible)
        expectant.append(900 * pregnant_eligible)
        foster_eligible.append(eligible)
        expectant_eligible.append(pregnant_eligible)
    return infant, expectant, foster_eligible, expectant_eligible


def _check_invariants(cases):
    situation, parent_indices = _situation(cases)
    simulation = Simulation(situation=situation)
    infant, expectant, foster_eligible, pregnant_eligible = _original_la_amounts(cases)
    expected = {
        "ca_la_infant_supplement": infant,
        "ca_la_expectant_parent_payment": expectant,
        "ca_foster_care_minor_dependent": foster_eligible,
        "ca_la_infant_supplement_eligible_person": foster_eligible,
        "ca_la_expectant_parent_payment_eligible": pregnant_eligible,
    }
    for year in YEARS:
        for variable, la_expected in expected.items():
            result = np.asarray(simulation.calculate(variable, f"{year}-01"))
            if variable != "ca_la_infant_supplement":
                result = result[parent_indices]
            result = result.reshape(len(cases), len(COUNTIES))

            # Changing the county preserves each California household's result.
            np.testing.assert_array_equal(
                result[:, : len(CA_COUNTIES)],
                np.repeat(result[:, [LA_INDEX]], len(CA_COUNTIES), axis=1),
            )
            # California payments and eligibility never extend to Nevada.
            np.testing.assert_array_equal(result[:, -1], 0)
            # LA retains main's age, placement, timing, child count and amounts.
            np.testing.assert_array_equal(result[:, LA_INDEX], la_expected)

            if variable in PAYMENTS:
                ineligible = np.array([not case["in_foster_care"] for case in cases])
                np.testing.assert_array_equal(result[ineligible], 0)
        # A default pregnancy month cannot qualify for an expectant payment.
        default_month = np.array([case["pregnancy_month"] is None for case in cases])
        expectant_result = simulation.calculate(
            "ca_la_expectant_parent_payment", f"{year}-01"
        )[parent_indices].reshape(len(cases), len(COUNTIES))
        np.testing.assert_array_equal(expectant_result[default_month], 0)


@settings(
    max_examples=4,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow],
)
@given(st.lists(foster_parent_cases(), min_size=1, max_size=4))
def test_ca_foster_payments_statewide_invariants(drawn_cases):
    _check_invariants(_boundary_cases() + drawn_cases)
