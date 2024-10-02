from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._apply_ssi_exclusions import (
    _apply_ssi_exclusions,
)


class ssi_income_deemed_from_ineligible_spouse(Variable):
    value_type = float
    entity = Person
    label = "SSI income (deemed from ineligible spouse)"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/20/416.1163"

    def formula(person, period, parameters):
        prereduction_personal_earned_income = person(
            "ssi_earned_income", period
        )
        blind_disabled_working_student_income = person(
            "ssi_blind_or_disabled_working_student_exclusion", period
        )
        personal_earned_income = max_(
            prereduction_personal_earned_income
            - blind_disabled_working_student_income,
            0,
        )
        personal_unearned_income = person("ssi_unearned_income", period)
        spousal_earned_income = person(
            "ssi_earned_income_deemed_from_ineligible_spouse", period
        )
        spousal_unearned_income = person(
            "ssi_unearned_income_deemed_from_ineligible_spouse", period
        )

        income_if_combined = _apply_ssi_exclusions(
            personal_earned_income + spousal_earned_income,
            personal_unearned_income + spousal_unearned_income,
            parameters,
            period,
        )

        income_if_not_combined = _apply_ssi_exclusions(
            personal_earned_income,
            personal_unearned_income,
            parameters,
            period,
        )

        spousal_deemed_income = income_if_combined - income_if_not_combined

        ssi = parameters(period).gov.ssa.ssi.amount
        person_rate = (
            person("is_ssi_ineligible_child", period)
            * (ssi.couple - ssi.individual)
            * MONTHS_IN_YEAR
        )

        return spousal_deemed_income * (spousal_deemed_income > person_rate)
