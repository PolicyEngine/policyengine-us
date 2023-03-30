from policyengine_us.model_api import *


class ny_tanf_countable_gross_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "New York TANF countable gross unearned income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NY

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ny.otda.tanf.income
        gross_unearned = add(spm_unit, period, p.unearned_income)
        enrolled = spm_unit("is_tanf_enrolled", period)
        return gross_unearned
