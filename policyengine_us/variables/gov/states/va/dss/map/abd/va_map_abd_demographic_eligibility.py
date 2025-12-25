from policyengine_us.model_api import *


class va_map_abd_demographic_eligibility(Variable):
    value_type = bool
    entity = SPMUnit
    label = "VA MAP ABD demographic eligiblity"
    definition_period = YEAR
    defined_for = StateCode.VA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.va.dss.map.abd.eligible_age
        person = spm_unit.members
        age = person("age", period)
        blind = person("is_blind", period)
        disabled = person("is_disabled", period)
        ssi = person("ssi", period)
        abd = ((age >= p) | blind | disabled) & (ssi == 0)

        return spm_unit.any(abd)
