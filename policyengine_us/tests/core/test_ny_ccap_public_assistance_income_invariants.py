"""Check New York CCAP income, public assistance and child care together."""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from policyengine_core.reforms import Reform

from policyengine_us import Simulation
from policyengine_us.model_api import SPMUnit, StateCode, Variable, YEAR, add, where
from policyengine_us.system import system as tax_benefit_system


YEARS = [2024, 2025, 2026]
TOLERANCE = 0.01
MAIN_INCOME_SOURCES = (
    "employment_income",
    "self_employment_income",
    "sstb_self_employment_income",
    "farm_operations_income",
    "social_security",
    "railroad_benefits",
    "dividend_income",
    "interest_income",
    "rental_income",
    "pension_income",
    "military_retirement_income",
    "total_unemployment_compensation",
    "strike_benefits",
    "workers_compensation",
    "alimony_income",
    "child_support_received",
    "veterans_benefits",
)
PROPERTY_SETTINGS = settings(
    max_examples=8,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


class MainCountableIncome(Reform):
    def apply(self):
        # Preserve main's formula and source list as the compatibility oracle.
        class ny_ccap_countable_income(Variable):
            value_type = float
            entity = SPMUnit
            definition_period = YEAR
            defined_for = StateCode.NY

            def formula(spm_unit, period, parameters):
                p = parameters(period).gov.states.ny.ocfs.ccap.income.countable_income
                countable = add(spm_unit, period, MAIN_INCOME_SOURCES)
                person = spm_unit.members
                is_child = person("is_child", period)
                adult_ssi = where(is_child, 0, add(person, period, ["ssi"]))
                excluded_earner = is_child & ~person("is_parent", period)
                excluded_earnings = where(
                    excluded_earner, add(person, period, p.earned_sources), 0
                )
                return countable + spm_unit.sum(adult_ssi - excluded_earnings)

        self.update_variable(ny_ccap_countable_income)


@pytest.fixture(scope="module")
def system():
    return tax_benefit_system


@pytest.fixture(scope="module")
def main_system(system):
    return MainCountableIncome(system)


@st.composite
def families(draw):
    child_age = draw(st.integers(0, 18))
    return {
        "earnings": draw(st.integers(0, 160_000)),
        "business_income": draw(st.integers(-20_000, 20_000)),
        "child_earnings": draw(st.integers(0, 15_000)),
        "child_age": child_age,
        "child_parent": child_age >= 12 and draw(st.booleans()),
        "adult_ssi": draw(st.integers(0, 1_000)),
        "child_ssi": draw(st.integers(0, 1_000)),
        "expenses": draw(st.integers(0, 4_000)),
        "market_rate": draw(st.integers(0, 4_000)),
        "in_care": draw(st.booleans()),
        "enrolled": draw(st.booleans()),
        "takeup": draw(st.booleans()),
        "low": draw(st.integers(0, 1_000)),
        "increase": draw(st.integers(1, 1_000)),
    }


def _monthly(year, amount):
    return {f"{year}-{month:02d}": amount for month in range(1, 13)}


def _situation(cases, year):
    situation = {
        "people": {},
        "tax_units": {},
        "spm_units": {},
        "families": {},
        "marital_units": {},
        "households": {},
    }
    for index, (family, amounts) in enumerate(cases):
        adult, child = f"adult_{index}", f"child_{index}"
        members = [adult, child]
        situation["people"][adult] = {
            "age": {year: 35},
            "is_parent": {year: True},
            "is_tax_unit_head": {year: True},
            "is_tax_unit_dependent": {year: False},
            "is_citizen_or_legal_immigrant": {year: True},
            "employment_income": {year: family["earnings"]},
            "self_employment_income": {year: family["business_income"]},
            "ssi": _monthly(year, family["adult_ssi"]),
            "ny_ssp": _monthly(year, amounts.get("adult_ssp", 0)),
            "childcare_hours_per_day": {year: 0},
            "ny_ccap_market_rate": _monthly(year, 0),
        }
        situation["people"][child] = {
            "age": {year: family["child_age"]},
            "is_parent": {year: family["child_parent"]},
            "is_tax_unit_head": {year: False},
            "is_tax_unit_dependent": {year: True},
            "is_citizen_or_legal_immigrant": {year: True},
            "employment_income": {year: family["child_earnings"]},
            "ssi": _monthly(year, family["child_ssi"]),
            "ny_ssp": _monthly(year, amounts.get("child_ssp", 0)),
            "childcare_hours_per_day": {year: 8 if family["in_care"] else 0},
            "childcare_days_per_week": {year: 5 if family["in_care"] else 0},
            "ny_ccap_market_rate": _monthly(year, family["market_rate"]),
        }
        unit = {
            "members": members,
            "ny_safety_net_assistance": _monthly(year, amounts.get("safety_net", 0)),
            "is_tanf_enrolled": _monthly(year, family["enrolled"]),
            "takes_up_tanf_if_eligible": {year: family["takeup"]},
            "meets_ccdf_activity_test": {year: True},
            "is_ccdf_asset_eligible": {year: True},
            "spm_unit_pre_subsidy_childcare_expenses": {year: 12 * family["expenses"]},
        }
        if amounts.get("family_assistance") is not None:
            unit["ny_tanf"] = _monthly(year, amounts["family_assistance"])
        situation["spm_units"][f"unit_{index}"] = unit
        for group in ("tax_units", "families"):
            situation[group][f"{group}_{index}"] = {"members": members}
        for person in members:
            situation["marital_units"][person] = {"members": [person]}
        situation["households"][f"household_{index}"] = {
            "members": members,
            "state_code": {year: "NY"},
            "county_str": {year: "NEW_YORK_COUNTY_NY"},
        }
    return situation


def _calculate(system, cases, year):
    simulation = Simulation(
        tax_benefit_system=system,
        situation=_situation(cases, year),
    )
    outputs = {
        "ny_ccap_countable_income": np.asarray(
            simulation.calculate("ny_ccap_countable_income", year)
        ),
        "ny_ccap_family_share": np.asarray(
            simulation.calculate("ny_ccap_family_share", f"{year}-10")
        ),
        "ny_ccap": np.asarray(simulation.calculate("ny_ccap", f"{year}-10")),
    }
    for name, values in outputs.items():
        assert np.isfinite(values).all(), f"{name} contains a nonfinite result"
    return outputs


@PROPERTY_SETTINGS
@given(st.sampled_from(YEARS), st.lists(families(), min_size=2, max_size=5))
def test_countable_income_weakly_rises_with_each_public_assistance_source(
    system, year, units
):
    cases = []
    expected_increases = []
    for family in units:
        for source in ("family_assistance", "safety_net", "adult_ssp"):
            for amount in (family["low"], family["low"] + family["increase"]):
                cases.append((family, {"family_assistance": 0, source: amount}))
            included = source != "family_assistance" or family["takeup"]
            expected_increases.append(12 * family["increase"] * included)
    income = _calculate(system, cases, year)["ny_ccap_countable_income"]
    increases = income[1::2] - income[0::2]
    assert (increases >= -TOLERANCE).all()
    np.testing.assert_allclose(increases, expected_increases, atol=TOLERANCE, rtol=0)


@PROPERTY_SETTINGS
@given(st.sampled_from(YEARS), st.lists(families(), min_size=2, max_size=6))
def test_zero_public_assistance_amounts_preserve_main_income_and_ccap(
    system, main_system, year, units
):
    cases = [(family, {"family_assistance": 0}) for family in units]
    actual = _calculate(system, cases, year)
    expected = _calculate(main_system, cases, year)
    for name in actual:
        np.testing.assert_allclose(
            actual[name], expected[name], atol=TOLERANCE, rtol=0, err_msg=name
        )


@PROPERTY_SETTINGS
@given(st.sampled_from(YEARS), st.lists(families(), min_size=2, max_size=6))
def test_a_childs_state_supplement_does_not_change_income_or_ccap(system, year, units):
    cases = []
    for family in units:
        minor_family = {**family, "child_age": min(family["child_age"], 17)}
        for supplement in (0, family["low"] + family["increase"]):
            cases.append(
                (minor_family, {"family_assistance": 0, "child_ssp": supplement})
            )
    outputs = _calculate(system, cases, year)
    for name, values in outputs.items():
        np.testing.assert_allclose(
            values[0::2], values[1::2], atol=TOLERANCE, rtol=0, err_msg=name
        )


@PROPERTY_SETTINGS
@given(st.sampled_from(YEARS), st.lists(families(), min_size=2, max_size=6))
def test_reported_public_assistance_keeps_the_family_share_zero(system, year, units):
    cases = [
        (
            {**family, "enrolled": True},
            {
                "family_assistance": family["low"] + family["increase"],
                "safety_net": family["low"],
                "adult_ssp": family["increase"],
            },
        )
        for family in units
    ]
    outputs = _calculate(system, cases, year)
    np.testing.assert_array_equal(outputs["ny_ccap_family_share"], 0)
    assert (outputs["ny_ccap"] >= 0).all()


@PROPERTY_SETTINGS
@given(st.sampled_from(YEARS), st.lists(families(), min_size=2, max_size=6))
def test_safety_net_receipt_alone_keeps_the_family_share_zero(system, year, units):
    if "ny_safety_net_assistance_received" not in system.variables:
        pytest.skip(
            "Safety Net receipt and its waiver require the categorical routes build."
        )
    cases = [
        (
            {**family, "enrolled": False, "takeup": False},
            {
                "family_assistance": 0,
                "safety_net": family["low"] + family["increase"],
            },
        )
        for family in units
    ]
    situation = _situation(cases, year)
    for unit in situation["spm_units"].values():
        unit["ny_safety_net_assistance_received"] = _monthly(year, True)
    simulation = Simulation(tax_benefit_system=system, situation=situation)
    np.testing.assert_array_equal(
        simulation.calculate("ny_ccap_family_share", f"{year}-10"), 0
    )


@pytest.mark.parametrize("year", YEARS)
def test_computed_family_assistance_with_childcare_expenses_avoids_federal_tanf(
    system, year
):
    family = {
        "earnings": 0,
        "business_income": 0,
        "child_earnings": 0,
        "child_age": 3,
        "child_parent": False,
        "adult_ssi": 0,
        "child_ssi": 0,
        "expenses": 1_000,
        "market_rate": 2_000,
        "in_care": True,
        "enrolled": True,
        "takeup": True,
    }
    situation = _situation([(family, {})], year)
    situation["people"]["adult_0"]["pre_subsidy_rent"] = {year: 12_000}
    situation["spm_units"]["unit_0"]["spm_unit_cash_assets"] = {year: 0}
    simulation = Simulation(tax_benefit_system=system, situation=situation)
    simulation.trace = True

    benefit = simulation.calculate("ny_ccap", f"{year}-10")
    grant = simulation.calculate("ny_tanf", f"{year}-10")
    income = simulation.calculate("ny_ccap_countable_income", year)

    assert (grant > 0).all()
    assert (benefit > 0).all()
    assert (benefit <= family["expenses"]).all()
    np.testing.assert_allclose(income, 12 * grant, atol=TOLERANCE, rtol=0)
    np.testing.assert_array_equal(
        simulation.calculate("ny_ccap_family_share", f"{year}-10"), 0
    )
    assert simulation.tracer.get_nb_requests("tanf") == 0
    assert simulation.tracer.get_nb_requests("tanf_if_takes_up") == 0
