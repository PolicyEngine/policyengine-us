from policyengine_us.model_api import *


class tn_ff_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Tennessee Families First countable earned income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.TN

    def formula(spm_unit, period, parameters):
        # Get gross earned income from federal TANF variable
        person = spm_unit.members
        gross_earned = spm_unit.sum(person("tanf_gross_earned_income", period))

        # Apply $250 earned income disregard per Tenn. Comp. R. & Regs. 1240-01-50
        p = parameters(period).gov.states.tn.dhs.ff.income.deductions
        earned_disregard = p.earned_income_disregard
        return max_(gross_earned - earned_disregard, 0)
