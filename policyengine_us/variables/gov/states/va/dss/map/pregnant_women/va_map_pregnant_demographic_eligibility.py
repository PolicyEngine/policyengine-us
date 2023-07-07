from policyengine_us.model_api import *


class va_map_pregnant_demographic_eligibility(Variable):
    value_type = bool
    entity = SPMUnit
    label = "VA MAP Pregnant Women demographic eligibility"
    definition_period = YEAR
    defined_for = StateCode.VA

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        pregnant = person("is_pregnant", period)
        unit_size = spm_unit("spm_unit_size", period)

        return (spm_unit.any(pregnant)) & (unit_size >= 2)
