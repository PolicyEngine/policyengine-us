from policyengine_us.model_api import *


class il_pi_has_geriatric_pregnancy(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Household has geriatric pregnancy for Illinois PI"
    definition_period = YEAR
    reference = "https://www.isbe.net/Documents/Prevention-Initiative-Eligibility-Form.pdf#page=3"
    defined_for = StateCode.IL

    def formula(spm_unit, period, parameters):
        # Factor 28: Pregnant woman age 40 or over
        p = parameters(period).gov.states.il.isbe.pi.eligibility.priority
        is_pregnant = spm_unit.members("is_pregnant", period)
        age = spm_unit.members("age", period)
        has_geriatric_pregnancy = is_pregnant & (
            age >= p.geriatric_pregnancy_age
        )
        return spm_unit.any(has_geriatric_pregnancy)
