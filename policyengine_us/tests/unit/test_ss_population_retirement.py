"""Retirement population record resolution without constructing a US model.

Only Person input arrays, stored-input metadata and a selector snapshot are
supplied here. The production adapter resolves eligibility and calls the real
shared cohort/claiming rules; no formula, parameter tree or simulation is copied.
"""

from fractions import Fraction
from types import SimpleNamespace

import numpy as np
import pytest
from policyengine_core.periods import period

from policyengine_us.tools.social_security.population import _record_basis
from policyengine_us.tools.social_security_benefit_levers import (
    SocialSecurityBenefitSource,
)


PERIOD = period(2026)


class PersonInputs:
    ids = ("retiree",)

    def __init__(self, **inputs):
        age = inputs.get("age", 62)
        values = {
            "age": age,
            "birth_year": 2026 - age,
            "social_security_retirement_reported": 12000,
            "social_security_retirement_source": SocialSecurityBenefitSource.reported,
            "social_security_retirement_worker_eligibility_year": 0,
            "social_security_retirement_worker_id": "",
            "social_security_worker_computation_year": 0,
            "social_security_retirement_entitlement_year": 0,
            "social_security_retirement_entitlement_month": 1,
            "social_security_retirement_claim_age_months": 744,
            "social_security_birth_month": 0,
            "social_security_birth_day": 0,
            "ss_calculator_birth_date": "",
            "social_security_survivors_reported": 0,
            "social_security_dependents_reported": 0,
            "social_security_disability_reported": 0,
            **inputs,
        }
        self.inputs = {name: np.asarray([value]) for name, value in values.items()}
        # Exercise the actual has_input helper, including the distinction
        # between supplied birth year and the ordinary age-derived formula.
        self.simulation = SimpleNamespace(
            tax_benefit_system=SimpleNamespace(
                variables={"birth_year": SimpleNamespace(definition_period="year")}
            ),
            _get_visible_branch_names=lambda: ("default",),
            _user_input_keys={("birth_year", "default", PERIOD)}
            if "birth_year" in inputs
            else set(),
        )

    def __call__(self, name, requested_period):
        assert requested_period == PERIOD
        return self.inputs[name]


def resolve(*, scenario="supplied_claim_age", **inputs):
    parameters = SimpleNamespace(
        gov=SimpleNamespace(
            contrib=SimpleNamespace(
                ssa=SimpleNamespace(
                    benefit_levers=SimpleNamespace(
                        pia_ratio=lambda when: SimpleNamespace(
                            claiming_scenario=[scenario]
                        )
                    )
                )
            )
        )
    )
    return _record_basis(PersonInputs(**inputs), PERIOD, parameters, "retirement")


def test_supplied_eligibility_cohort_precedes_an_age_derived_birth_year():
    result = resolve(
        age=70,
        social_security_retirement_worker_eligibility_year=2015,
    )
    assert result["eligibility_year"][0] == 2015
    assert result["claiming_adjustment"][0] == Fraction(3, 4)
    assert not result["missing_claim_age"][0]


def test_supplied_birth_year_precedes_the_current_age_proxy():
    result = resolve(age=70, birth_year=1964)
    assert result["eligibility_year"][0] == 2026
    assert result["claiming_adjustment"][0] == Fraction(7, 10)


@pytest.mark.parametrize(
    ("scenario", "adjustment"),
    [("supplied_claim_age", Fraction(13, 15)), ("fra", Fraction(1))],
)
def test_observed_claim_identifies_one_cohort_across_sensitivity_scenarios(
    scenario, adjustment
):
    result = resolve(
        scenario=scenario,
        age=70,
        social_security_retirement_entitlement_year=2025,
        social_security_retirement_entitlement_month=6,
        social_security_retirement_claim_age_months=780,
    )
    assert result["eligibility_year"][0] == 2022
    assert result["claiming_adjustment"][0] == adjustment
    assert result["proxy"][0]


def test_supplied_birth_month_and_day_do_not_identify_a_missing_birth_year():
    result = resolve(
        social_security_birth_month=6,
        social_security_birth_day=15,
        social_security_retirement_claim_age_months=747,
    )
    assert result["eligibility_year"][0] == 2026
    assert result["claiming_adjustment"][0] == Fraction(57, 80)
    assert result["proxy"][0]


def test_entitlement_dates_accept_birth_month_without_day_as_a_proxy():
    result = resolve(
        scenario="entitlement_dates",
        birth_year=1964,
        social_security_birth_month=6,
        social_security_retirement_entitlement_year=2026,
        social_security_retirement_entitlement_month=9,
    )
    assert result["eligibility_year"][0] == 2026
    assert result["claiming_adjustment"][0] == Fraction(57, 80)
    assert not result["missing_claim_age"][0]
    assert result["proxy"][0]


def test_missing_supplied_claim_age_has_no_actuarial_default():
    result = resolve(social_security_retirement_claim_age_months=0)
    assert result["claiming_adjustment"][0] == 0
    assert result["missing_claim_age"][0]
    assert result["unmodeled"][0]


@pytest.mark.parametrize(
    ("scenario", "adjustment"),
    (
        ("age_62", Fraction(11, 15)),
        ("age_65", Fraction(41, 45)),
        ("fra", Fraction(1)),
        ("age_70", Fraction(97, 75)),
    ),
)
def test_imputed_claiming_scenario_is_flagged_with_exact_birth(scenario, adjustment):
    # Born in 1956: FRA is 796 months. At 62 the reduction is
    # 36/180 + 16/240; at 65 it is 16/180; at 70 the credit is 44/150.
    result = resolve(
        scenario=scenario,
        age=70,
        ss_calculator_birth_date="1956-06-15",
        social_security_retirement_claim_age_months=0,
    )
    assert not result["unmodeled"][0]
    assert result["eligibility_year"][0] == 2018
    assert result["claiming_adjustment"][0] == adjustment
    assert result["proxy"][0]


@pytest.mark.parametrize("scenario", ("supplied_claim_age", "entitlement_dates"))
def test_observed_claiming_sources_keep_exact_birth_identified(scenario):
    result = resolve(
        scenario=scenario,
        age=70,
        ss_calculator_birth_date="1956-06-15",
        social_security_retirement_claim_age_months=780,
        social_security_retirement_entitlement_year=2021,
        social_security_retirement_entitlement_month=6,
    )
    assert not result["unmodeled"][0]
    assert result["eligibility_year"][0] == 2018
    assert result["claiming_adjustment"][0] == Fraction(41, 45)
    assert not result["proxy"][0]


def test_zero_benefit_bypasses_record_fields_and_parameter_reads():
    def zero_person(name, requested_period):
        assert requested_period == PERIOD
        return {
            "social_security_retirement_reported": np.array([0]),
            "social_security_retirement_source": np.array(
                [SocialSecurityBenefitSource.reported]
            ),
        }[name]

    result = _record_basis(zero_person, PERIOD, None, "retirement")
    assert result["eligibility_year"][0] == 0
    assert result["claiming_adjustment"][0] == 1
    assert not result["positive"][0]
    assert not result["missing_claim_age"][0]
    assert not result["unmodeled"][0]
