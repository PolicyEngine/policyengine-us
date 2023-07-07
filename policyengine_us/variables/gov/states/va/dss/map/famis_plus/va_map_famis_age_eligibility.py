from policyengine_us.model_api import *


class va_map_famis_age_eligibility(Variable):
    value_type = bool
    entity = SPMUnit
    label = "VA MAP FAMIS Plus age eligibility"
    definition_period = YEAR
    defined_for = StateCode.VA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.va.dss.map.famis_plus.eligible_age
        person = spm_unit.members
        child = person("is_child", period)
        age = person("age", period)

        return spm_unit.any((age <= p) & (child))
