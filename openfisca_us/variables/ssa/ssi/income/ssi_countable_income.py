from openfisca_us.model_api import *


class ssi_countable_income(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = "Supplemental Security Income countable income"
    label = "SSI countable income"
    unit = USD

    def formula(person, period, parameters):
        earned = person("ssi_earned_income", period) / 12
        unearned = person("ssi_unearned_income", period) / 12
        deemed = person("ssi_deemed_income", period) / 12
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
        return (countable_unearned + countable_earned + deemed) * 12
