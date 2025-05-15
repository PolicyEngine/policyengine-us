from policyengine_us.model_api import *


class il_tanf_countable_gross_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Illinois Temporary Assistance for Needy Families (TANF) countable gross earned income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.IL

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        gross_earned_income = person("il_tanf_gross_earned_income", period)
        return spm_unit.sum(is_head_or_spouse * gross_earned_income)
