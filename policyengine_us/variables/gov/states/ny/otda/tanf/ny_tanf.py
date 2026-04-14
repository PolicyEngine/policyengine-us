from policyengine_us.model_api import *


class ny_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "New York TANF"
    unit = USD
    definition_period = MONTH
    defined_for = "ny_tanf_eligible"

    def formula(spm_unit, period, parameters):
        need_standard = spm_unit("ny_tanf_need_standard", period)
        income = spm_unit("ny_tanf_countable_income", period)
        benefit = max_(need_standard - income, 0)
        return min_(benefit, need_standard)
