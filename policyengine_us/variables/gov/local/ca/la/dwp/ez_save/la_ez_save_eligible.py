from policyengine_us.model_api import *


class la_ez_save_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Eligible for the Los Angeles County EZ Save program"
    defined_for = "in_la"

    def formula(spm_unit, period, parameters):
        income = spm_unit("la_ez_save_countable_income", period)
        household_size = spm_unit("spm_unit_size", period)
        p = parameters(
            period
        ).gov.local.ca.la.dwp.ez_save.eligibility.income_threshold
        # The income threshold is increased for each member of the household over a certain size
        applicable_household_size = max_(
            household_size - p.base.household_size, 0
        )
        income_threshold_increase = (
            p.increase_increment * applicable_household_size
        )
        income_threshold = p.base.amount + income_threshold_increase
        return income <= income_threshold
