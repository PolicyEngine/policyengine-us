from policyengine_us.model_api import *


class nm_tanf_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "New Mexico TANF countable earned income"
    unit = USD
    definition_period = MONTH
    reference = "https://www.srca.nm.gov/parts/title08/08.102.0520.html"
    defined_for = StateCode.NM

    def formula(spm_unit, period, parameters):
        gross_earned = add(spm_unit, period, ["tanf_gross_earned_income"])
        earned_deduction = spm_unit("nm_tanf_earned_income_deduction", period)
        return max_(gross_earned - earned_deduction, 0)
