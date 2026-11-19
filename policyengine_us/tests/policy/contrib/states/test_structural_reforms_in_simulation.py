"""State structural reforms must build and calculate in a real ``Simulation``.

YAML tests apply a reform once, to a copy of the built default system. A
``Simulation`` instead builds ``CountryTaxBenefitSystem(reform=...)``, which
finds structural reforms from their ``in_effect`` parameters and refreshes the
per-capita uprating series, and then applies the reforms a second time. The
failures covered here only appear on that path, so YAML tests cannot detect
them.
"""

from functools import lru_cache
from types import SimpleNamespace

import numpy as np
import pytest
from policyengine_core.reforms import Reform

from policyengine_us import Simulation
from policyengine_us.reforms.states.nd.eitc.nd_eitc_reform import (
    create_nd_eitc_reform,
)
from policyengine_us.reforms.states.ut.ut_hb210_s2 import ut_hb210_s2
from policyengine_us.system import DEFAULT_START_DATE, system
from policyengine_us.tools.per_capita_uprating import (
    is_national_total_path,
    per_capita_path,
)

PERIOD = "2026"
REFORM_DATES = "2024-01-01.2100-12-31"
FEDERAL_EITC = 1_000
EITC_MATCH_RATE = 0.5
# gov.states.oh.tax.income.credits.eitc.rate
OHIO_EITC_RATE = 0.3
EMPLOYMENT_INCOME_NATIONAL_TOTAL = "calibration.gov.irs.soi.employment_income"
EXPECTED_REFUNDABLE_CREDIT_BY_STATE = {
    "AL": FEDERAL_EITC * EITC_MATCH_RATE,
    "KY": FEDERAL_EITC * EITC_MATCH_RATE,
    "MS": FEDERAL_EITC * EITC_MATCH_RATE,
    "ND": FEDERAL_EITC * EITC_MATCH_RATE,
    # Ohio's reform has no match rate: it refunds Ohio's existing credit.
    "OH": FEDERAL_EITC * OHIO_EITC_RATE,
}
UTAH_MARRIAGE_CREDIT_SWITCH = "gov.contrib.states.ut.hb210.s2_marriage_credit.in_effect"
# JOINT entry of gov.contrib.states.ut.hb210.s2_marriage_credit.amount
UTAH_JOINT_MARRIAGE_CREDIT = 158


def _eitc_reform_parameters():
    reform_parameters = {}
    for state_code in EXPECTED_REFUNDABLE_CREDIT_BY_STATE:
        eitc_parameters = (
            f"gov.contrib.states.{state_code.lower()}"
            ".child_poverty_impact_dashboard.eitc"
        )
        reform_parameters[f"{eitc_parameters}.in_effect"] = {REFORM_DATES: True}
        if state_code != "OH":
            reform_parameters[f"{eitc_parameters}.match"] = {
                REFORM_DATES: EITC_MATCH_RATE
            }
    return reform_parameters


def _one_filer_per_state(state_codes, year=PERIOD):
    def groups_of_one(group_name):
        return {
            f"{group_name}_{state_code}": {"members": [state_code]}
            for state_code in state_codes
        }

    tax_units = groups_of_one("tax_unit")
    households = groups_of_one("household")
    for state_code in state_codes:
        tax_units[f"tax_unit_{state_code}"]["eitc"] = {year: FEDERAL_EITC}
        households[f"household_{state_code}"]["state_code"] = {year: state_code}
    return {
        "people": {state_code: {"age": {year: 35}} for state_code in state_codes},
        "tax_units": tax_units,
        "families": groups_of_one("family"),
        "spm_units": groups_of_one("spm_unit"),
        "marital_units": groups_of_one("marital_unit"),
        "households": households,
    }


def _utah_married_couple():
    spouses = ["spouse_with_earnings", "other_spouse"]
    return {
        "people": {
            "spouse_with_earnings": {
                "age": {PERIOD: 40},
                "employment_income": {PERIOD: 60_000},
            },
            "other_spouse": {"age": {PERIOD: 40}},
        },
        "tax_units": {
            "tax_unit": {"members": spouses, "filing_status": {PERIOD: "JOINT"}}
        },
        "families": {"family": {"members": spouses}},
        "spm_units": {"spm_unit": {"members": spouses}},
        "marital_units": {"marital_unit": {"members": spouses}},
        "households": {"household": {"members": spouses, "state_code": {PERIOD: "UT"}}},
    }


@lru_cache(maxsize=None)
def _baseline_utah_non_refundable_credits():
    baseline_simulation = Simulation(situation=_utah_married_couple())
    baseline_credits = baseline_simulation.calculate(
        "ut_non_refundable_credits", PERIOD
    )
    return float(np.asarray(baseline_credits)[0])


def _parameters_with_north_dakota_eitc_on_only_in(year):
    # Clone only the states subtree, so the test builds no full parameter tree.
    states = system.parameters.gov.contrib.states.clone()
    states.parent = None
    states.nd.child_poverty_impact_dashboard.eitc.in_effect.update(
        period=f"year:{year}:1", value=True
    )
    return SimpleNamespace(gov=SimpleNamespace(contrib=SimpleNamespace(states=states)))


@pytest.mark.parametrize("switch_year", [2024, 2025, 2033])
def test_reform_is_found_when_switch_is_on_in_a_checked_year(switch_year):
    parameters = _parameters_with_north_dakota_eitc_on_only_in(switch_year)

    assert create_nd_eitc_reform(parameters, DEFAULT_START_DATE) is not None


@pytest.mark.parametrize("switch_year", [2023, 2034])
def test_reform_is_not_found_when_switch_is_on_outside_checked_years(switch_year):
    parameters = _parameters_with_north_dakota_eitc_on_only_in(switch_year)

    assert create_nd_eitc_reform(parameters, DEFAULT_START_DATE) is None


def test_reform_on_only_before_the_default_year_applies_in_a_simulation():
    year = "2025"
    dates = "2025-01-01.2025-12-31"
    eitc_parameters = "gov.contrib.states.nd.child_poverty_impact_dashboard.eitc"
    simulation = Simulation(
        situation=_one_filer_per_state(["ND"], year=year),
        reform={
            f"{eitc_parameters}.in_effect": {dates: True},
            f"{eitc_parameters}.match": {dates: EITC_MATCH_RATE},
        },
    )

    credit = simulation.calculate("nd_refundable_credits", year)
    assert np.asarray(credit) == pytest.approx([FEDERAL_EITC * EITC_MATCH_RATE])


def test_eitc_reforms_that_replace_input_credits_build_and_calculate():
    """Each reform turns an uprated dollar input into a computed variable.

    All five states share one simulation, so the test builds one system.
    """
    state_codes = list(EXPECTED_REFUNDABLE_CREDIT_BY_STATE)
    simulation = Simulation(
        situation=_one_filer_per_state(state_codes),
        reform=_eitc_reform_parameters(),
    )

    for filer_index, state_code in enumerate(state_codes):
        expected_credits = np.zeros(len(state_codes))
        expected_credits[filer_index] = EXPECTED_REFUNDABLE_CREDIT_BY_STATE[state_code]
        calculated_credits = simulation.calculate(
            f"{state_code.lower()}_refundable_credits", PERIOD
        )
        assert np.asarray(calculated_credits) == pytest.approx(expected_credits)

    # The build only fails for a computed variable left on a national total, so
    # check that this test still exercises that case.
    variables = simulation.tax_benefit_system.variables
    for state_code in state_codes:
        credit_variable = variables[f"{state_code.lower()}_refundable_credits"]
        assert not credit_variable.is_input_variable()
        assert is_national_total_path(credit_variable.uprating)
    assert variables["employment_income_before_lsr"].uprating == per_capita_path(
        EMPLOYMENT_INCOME_NATIONAL_TOTAL
    )


@pytest.mark.parametrize(
    "includes_reform_object",
    [False, True],
    ids=["parameter_switch", "reform_object_and_parameter_switch"],
)
def test_utah_marriage_credit_reform_can_be_applied_repeatedly(
    includes_reform_object,
):
    switch_parameters = {UTAH_MARRIAGE_CREDIT_SWITCH: {REFORM_DATES: True}}
    reform = switch_parameters
    if includes_reform_object:
        reform = (
            ut_hb210_s2,
            Reform.from_dict(switch_parameters, country_id="us"),
        )

    simulation = Simulation(situation=_utah_married_couple(), reform=reform)

    marriage_credit = simulation.calculate("ut_hb210_s2_marriage_credit", PERIOD)
    assert np.asarray(marriage_credit) == pytest.approx([UTAH_JOINT_MARRIAGE_CREDIT])
    non_refundable_credits = (
        simulation.tax_benefit_system.parameters.gov.states.ut.tax.income.credits
    ).non_refundable(f"{PERIOD}-01-01")
    assert list(non_refundable_credits).count("ut_hb210_s2_marriage_credit") == 1

    reformed_credits = np.asarray(
        simulation.calculate("ut_non_refundable_credits", PERIOD)
    )
    credit_increase = reformed_credits - _baseline_utah_non_refundable_credits()
    assert credit_increase == pytest.approx([UTAH_JOINT_MARRIAGE_CREDIT])
