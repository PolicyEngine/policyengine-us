from policyengine_us.model_api import *


class ms_ccpp_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Mississippi CCPP countable income"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.MS
    reference = "https://www.mdhs.ms.gov/wp-content/uploads/2026/01/CCPP-Policy-Manual_Final_1142025.pdf#page=28"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ms.dhs.ccpp.income
        earned = add(spm_unit, period, ["ms_ccpp_countable_earned_income"])
        unearned = add(spm_unit, period, p.countable_income.unearned_sources)
        return earned + unearned
