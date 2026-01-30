from policyengine_us.model_api import *


class tn_ff_earned_income_after_disregard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Tennessee Families First earned income after disregard"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.TN
    reference = "https://publications.tnsosfiles.com/rules/1240/1240-01/1240-01-50.20081124.pdf#page=19"

    def formula(spm_unit, period, parameters):
        gross_earned = add(spm_unit, period, ["tanf_gross_earned_income"])
        p = parameters(period).gov.states.tn.dhs.ff.income.deductions
        return max_(gross_earned - p.earned_income_disregard, 0)
