from policyengine_us.model_api import *


class il_pi_has_developmental_delay(Variable):
    value_type = bool
    entity = SPMUnit
    label = "SPM unit has developmental delay or disability for Illinois PI"
    definition_period = YEAR
    reference = "https://www.isbe.net/Documents/Prevention-Initiative-Eligibility-Form.pdf#page=2"
    defined_for = StateCode.IL

    def formula(spm_unit, period, parameters):
        # Factor 18: Member of household has developmental delay or disability
        has_disability = spm_unit.members("is_disabled", period)
        has_dev_delay = spm_unit.members("has_developmental_delay", period)
        return spm_unit.any(has_disability | has_dev_delay)
