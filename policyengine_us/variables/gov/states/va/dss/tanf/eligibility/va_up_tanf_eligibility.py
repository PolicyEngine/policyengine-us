from policyengine_us.model_api import *


class va_up_tanf_eligibility(Variable):
    value_type = bool
    entity = SPMUnit
    label = "VA UP-TANF eligibility"
    definition_period = YEAR
    defined_for = StateCode.VA
    reference = "https://www.dss.virginia.gov/files/division/bp/tanf/manual/300_11-20.pdf#page=3"

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        earned_income = person("earned_income", period)
        father = person("is_father", period)
        mother = person("is_mother", period)
        disabled = person("is_disabled", period)
        eligible_father = (father) & (~disabled) & (earned_income == 0)
        eligible_mother = (mother) & (~disabled) & (earned_income == 0)
        return spm_unit.any(eligible_father) & spm_unit.any(eligible_mother)
