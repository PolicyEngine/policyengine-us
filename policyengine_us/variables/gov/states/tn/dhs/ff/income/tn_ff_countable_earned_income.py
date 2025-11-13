from policyengine_us.model_api import *


class tn_ff_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Tennessee Families First countable earned income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.TN

    def formula(spm_unit, period, parameters):
        gross_earned = add(spm_unit, period, ["tanf_gross_earned_income"])
        p = parameters(period).gov.states.tn.dhs.ff.income.deductions
        return max_(gross_earned - p.earned_income_disregard, 0)
