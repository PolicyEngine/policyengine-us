from policyengine_us.model_api import *


class sd_tanf_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "South Dakota TANF countable earned income"
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/south-dakota/ARSD-67-10-03-05"
    defined_for = StateCode.SD

    def formula(spm_unit, period, parameters):
        gross_earned = spm_unit("tanf_gross_earned_income", period)
        p = parameters(
            period
        ).gov.states.sd.dss.tanf.income.earned_income_disregard
        after_flat = max_(gross_earned - p.flat_deduction, 0)
        return after_flat * (1 - p.percentage)
