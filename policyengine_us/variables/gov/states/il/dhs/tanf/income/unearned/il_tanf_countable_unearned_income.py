from policyengine_us.model_api import *


class il_tanf_countable_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Illinois Temporary Assistance for Needy Families (TANF) countable unearned income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.IL
    reference = "http://law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-112.101"

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        gross_unearned_income = person("il_tanf_gross_unearned_income", period)
        return spm_unit.sum(is_head_or_spouse * gross_unearned_income)
