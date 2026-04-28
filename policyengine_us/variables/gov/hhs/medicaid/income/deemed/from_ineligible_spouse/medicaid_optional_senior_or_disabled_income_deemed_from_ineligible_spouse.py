from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.medicaid.income._apply_medicaid_optional_senior_or_disabled_exclusions import (
    _apply_medicaid_optional_senior_or_disabled_exclusions,
)


class medicaid_optional_senior_or_disabled_income_deemed_from_ineligible_spouse(
    Variable
):
    value_type = float
    entity = Person
    label = "Medicaid optional senior or disabled income deemed from ineligible spouse"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/20/416.1163"
    defined_for = "is_ssi_eligible_individual"
    unit = USD

    def formula(person, period, parameters):
        deeming_applies = person("is_ssi_spousal_deeming_applies", period)
        spouse_earned = person(
            "ssi_earned_income_deemed_from_ineligible_spouse", period
        )
        spouse_unearned = person(
            "ssi_unearned_income_deemed_from_ineligible_spouse", period
        )
        individual_earned = person("ssi_earned_income", period)
        individual_unearned = person("ssi_unearned_income", period)

        p = parameters(
            period
        ).gov.hhs.medicaid.eligibility.categories.senior_or_disabled.income.disregard
        state = person.household("state_code_str", period)

        alone_countable = _apply_medicaid_optional_senior_or_disabled_exclusions(
            individual_earned,
            individual_unearned,
            state,
            p.individual[state],
            parameters,
            period,
        )
        couple_countable = _apply_medicaid_optional_senior_or_disabled_exclusions(
            individual_earned + spouse_earned,
            individual_unearned + spouse_unearned,
            state,
            p.couple[state],
            parameters,
            period,
        )

        deemed_amount = max_(0, couple_countable - alone_countable)
        return deeming_applies * deemed_amount
