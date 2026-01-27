from policyengine_us.model_api import *


class va_up_tanf_eligibility(Variable):
    value_type = bool
    entity = SPMUnit
    label = "VA TANF-UP eligibility"
    definition_period = MONTH
    defined_for = StateCode.VA
    reference = "https://www.dss.virginia.gov/files/division/bp/tanf/manual/700_07-20.pdf#page=2"

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        disabled = person("is_disabled", period.this_year)
        able_bodied_adult = head_or_spouse & ~disabled
        return spm_unit.sum(able_bodied_adult) > 1
