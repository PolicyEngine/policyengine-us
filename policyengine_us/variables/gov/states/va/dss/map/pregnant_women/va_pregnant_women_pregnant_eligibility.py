from policyengine_us.model_api import *


class va_pregnant_women_pregnant_eligibility(Variable):
    value_type = bool
    entity = SPMUnit
    label = "VA Pregnant Women Pregnant Eligibility"
    definition_period = YEAR
    defined_for = StateCode.VA

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        pregnant = person("is_pregnant", period)
        unit_size = spm_unit("spm_unit_size", period)

        return (spm_unit.any(pregnant)) & (unit_size >= 2)
