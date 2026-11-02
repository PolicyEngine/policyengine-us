from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._apply_ssi_exclusions import (
    _apply_ssi_exclusions,
)


class medicaid_medically_needy_income_from_spouse(Variable):
    value_type = float
    entity = Person
    label = "Spouse income counted by a state that budgets a couple together"
    unit = USD
    documentation = (
        "Countable income added for an ineligible spouse in a state that budgets "
        "a couple together, when SSI deeming has not already counted it."
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/42/435.602"

    def formula(person, period, parameters):
        state = person.household("state_code_str", period)
        p = parameters(
            period
        ).gov.hhs.medicaid.eligibility.categories.medically_needy.limit.income
        budgets_together = p.budgets_couple_together[state].astype(bool)
        marital_unit = person.marital_unit
        ineligible_spouse = person("is_ssi_ineligible_spouse", period)
        earned = person("ssi_earned_income", period)
        unearned = person("ssi_unearned_income", period)
        spouse_earned = (
            marital_unit.sum(ineligible_spouse * earned) - ineligible_spouse * earned
        )
        spouse_unearned = (
            marital_unit.sum(ineligible_spouse * unearned)
            - ineligible_spouse * unearned
        )
        alone = _apply_ssi_exclusions(earned, unearned, parameters, period)
        combined = _apply_ssi_exclusions(
            earned + spouse_earned, unearned + spouse_unearned, parameters, period
        )
        applies = (
            budgets_together
            & person("is_ssi_aged_blind_disabled", period)
            & ~person("is_ssi_spousal_deeming_applies", period)
        )
        return where(applies, max_(combined - alone, 0), 0)
