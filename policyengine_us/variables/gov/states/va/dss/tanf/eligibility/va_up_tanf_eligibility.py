from policyengine_us.model_api import *


class va_up_tanf_eligibility(Variable):
    value_type = bool
    entity = SPMUnit
    label = "VA UP-TANF eligibility"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.VA

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        earned_income = person("earned_income", period)
        mother = person("is_mother", period)
        father = person("is_father", period)
        disabled = person("is_disabled", period)
        eligible_father = (father) & (~disabled) & (earned_income == 0)
        eligible_mother = (mother) & (~disabled) & (earned_income == 0)
        return spm_unit.any(eligible_father & eligible_mother)
