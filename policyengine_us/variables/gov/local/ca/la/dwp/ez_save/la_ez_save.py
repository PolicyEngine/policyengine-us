from policyengine_us.model_api import *


class la_ez_save(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "Los Angeles County EZ Save program"
    defined_for = "la_ez_save_eligible"

    def formula(spm_unit, period, parameters):
        electricity_expense = spm_unit("electricity_expense", period)
        p = parameters(period).gov.local.ca.la.dwp.ez_save
        uncapped_amount = p.amount * MONTHS_IN_YEAR
        return min_(electricity_expense, uncapped_amount)
