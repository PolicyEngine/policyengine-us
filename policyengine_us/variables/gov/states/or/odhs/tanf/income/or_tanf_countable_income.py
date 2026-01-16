from policyengine_us.model_api import *


class or_tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Oregon TANF countable income"
    unit = USD
    definition_period = MONTH
    reference = "https://oregon.public.law/rules/oar_461-140-0010"
    defined_for = StateCode.OR

    def formula(spm_unit, period, parameters):
        gross_earned = add(spm_unit, period, ["tanf_gross_earned_income"])
        gross_unearned = add(spm_unit, period, ["tanf_gross_unearned_income"])
        child_support_disregard = spm_unit(
            "or_tanf_child_support_disregard", period
        )
        countable_unearned = max_(gross_unearned - child_support_disregard, 0)
        return gross_earned + countable_unearned
