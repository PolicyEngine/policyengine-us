from policyengine_us.model_api import *


class dc_ccsp_is_full_time(Variable):
    value_type = bool
    entity = Person
    label = "Person is attending full time day care under DC Child Care Subsidy Program (CCSP)"
    definition_period = MONTH
    defined_for = StateCode.DC

    def formula(person, period, parameters):
        p = parameters(period).gov.states.dc.dhs.ccsp
        schedule_type = person("dc_ccsp_schedule_type", period)
        schedule_type_str = schedule_type.decode_to_str()
        return np.isin(
            schedule_type_str,
            p.full_time_schedule_types,
        )
