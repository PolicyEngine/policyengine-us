from policyengine_us.model_api import *


class tn_tanf_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Tennessee TANF countable earned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/tennessee/Tenn-Comp-R-Regs-1240-01-50",
        "Tennessee Administrative Code § 1240-01-50 - Financial Eligibility Requirements",
        "Tennessee TANF State Plan 2024-2027",
    )
    defined_for = StateCode.TN

    def formula(spm_unit, period, parameters):
        gross_earned = spm_unit("tn_tanf_gross_earned_income", period)
        p = parameters(period).gov.states.tn.dhs.tanf.income.deductions
        earned_disregard = p.earned_income_disregard
        # Apply $250 earned income disregard
        return max_(gross_earned - earned_disregard, 0)
