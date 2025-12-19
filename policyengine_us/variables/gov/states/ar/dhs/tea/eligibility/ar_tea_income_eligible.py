from policyengine_us.model_api import *


class ar_tea_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Arkansas TEA income eligible"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/arkansas/208-00-13-Ark-Code-R-SS-001"
    defined_for = StateCode.AR

    def formula(spm_unit, period, parameters):
        # Per 208.00.13 Ark. Code R. Section 001, Section 3.3
        p = parameters(period).gov.states.ar.dhs.tea.income
        # Countable income must be at or below the income limit
        countable_income = spm_unit("ar_tea_countable_income", period)
        return countable_income <= p.income_limit
