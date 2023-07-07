from policyengine_us.model_api import *


class va_map_pregnant_eligibility(Variable):
    value_type = bool
    entity = SPMUnit
    label = "VA MAP Pregnant Women eligibility"
    definition_period = YEAR
    defined_for = StateCode.VA

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        ssi_recipient = person("ssi", period) > 0
        return spm_unit.any(ssi_recipient)