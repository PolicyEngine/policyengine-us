from openfisca_us.model_api import *


class ssi_ineligible_spouse_countable_income(Variable):
    value_type = float
    entity = Person
    label = "SSI countable income (ineligible spouse)"
    definition_period = YEAR

    def formula(person, period, parameters):
        earned = person("ssi_personal_earned_income", period) / MONTHS_IN_YEAR
        unearned = (
            person("ssi_personal_unearned_income", period) / MONTHS_IN_YEAR
        )
        # Deduct exclusions.
        exclusions = parameters(period).ssa.ssi.income.exclusions
        # Subtract from unearned income first.
        unearned_exclusion = min_(exclusions.general, unearned)
        countable_unearned = unearned - unearned_exclusion
        # Remaining general exclusion is treated as an earned income exclusion.
        remaining_general_exclusion = exclusions.general - unearned_exclusion
        earned_exclusion = exclusions.earned + remaining_general_exclusion
        # Subtract the percentage of earned income above the flat exclusion.
        earned_after_flat_exclusion = max_(earned - earned_exclusion, 0)
        countable_earned_share = 1 - exclusions.earned_share
        countable_earned = earned_after_flat_exclusion * countable_earned_share
        eligible = person("is_ssi_aged_blind_disabled", period)
        ineligible_spouse = person.marital_unit.any(eligible) & ~eligible
        return (
            ineligible_spouse
            * (countable_unearned + countable_earned)
            * MONTHS_IN_YEAR
        )
