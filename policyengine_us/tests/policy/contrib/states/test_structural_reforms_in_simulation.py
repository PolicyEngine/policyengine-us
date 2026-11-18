"""State structural reforms must build and calculate in a real ``Simulation``.

YAML tests apply a reform once, to a copy of the built default system. A
``Simulation`` instead builds ``CountryTaxBenefitSystem(reform=...)``, which
finds structural reforms from their ``in_effect`` parameters and refreshes the
per-capita uprating series, and then applies the reforms a second time. The
failures covered here only appear on that path, so YAML tests cannot detect
them.
"""

import numpy as np
import pytest
from policyengine_core.reforms import Reform

from policyengine_us import Simulation
from policyengine_us.reforms.states.ut.ut_hb210_s2 import ut_hb210_s2

PERIOD = "2026"
REFORM_DATES = "2024-01-01.2100-12-31"
FEDERAL_EITC = 1_000
EITC_MATCH_RATE = 0.5
OHIO_EITC_RATE = 0.3
EXPECTED_REFUNDABLE_CREDIT_BY_STATE = {
    "AL": FEDERAL_EITC * EITC_MATCH_RATE,
    "KY": FEDERAL_EITC * EITC_MATCH_RATE,
    "MS": FEDERAL_EITC * EITC_MATCH_RATE,
    "ND": FEDERAL_EITC * EITC_MATCH_RATE,
    # Ohio's reform has no match rate: it refunds Ohio's existing credit.
    "OH": FEDERAL_EITC * OHIO_EITC_RATE,
}
UTAH_MARRIAGE_CREDIT_SWITCH = "gov.contrib.states.ut.hb210.s2_marriage_credit.in_effect"
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


def _one_filer_per_state(state_codes):
    def groups_of_one(group_name):
        return {
            f"{group_name}_{state_code}": {"members": [state_code]}
            for state_code in state_codes
        }

    tax_units = groups_of_one("tax_unit")
    households = groups_of_one("household")
    for state_code in state_codes:
        tax_units[f"tax_unit_{state_code}"]["eitc"] = {PERIOD: FEDERAL_EITC}
        households[f"household_{state_code}"]["state_code"] = {PERIOD: state_code}
    return {
        "people": {state_code: {"age": {PERIOD: 35}} for state_code in state_codes},
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
