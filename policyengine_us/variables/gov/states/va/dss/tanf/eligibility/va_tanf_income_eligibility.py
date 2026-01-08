from policyengine_us.model_api import *


class va_tanf_income_eligibility(Variable):
    value_type = bool
    entity = SPMUnit
    label = "VA TANF income eligibility"
    definition_period = YEAR
    defined_for = StateCode.VA
    reference = "https://www.dss.virginia.gov/files/division/bp/tanf/manual/300_11-20.pdf#page=47"

    def formula(spm_unit, period, parameters):
        # Care expenses must be disregarded in both initial eligibility
        # and payment calculation per manual page 50 section 5.
        income = spm_unit("va_tanf_countable_income", period)
        need_standard = spm_unit("va_tanf_need_standard", period)
        return income <= need_standard
