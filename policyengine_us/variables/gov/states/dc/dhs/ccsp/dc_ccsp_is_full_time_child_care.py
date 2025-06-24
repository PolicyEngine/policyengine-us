from policyengine_us.model_api import *


class dc_ccsp_is_full_time_child_care(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Whether the person is attending the child care center full time in DC Child Care Subsidy Program (CCSP)"
    defined_for = StateCode.DC

    def formula(person, period, parameters):
        p = parameters(period).gov.states.dc.dhs.ccsp
        hours_per_day = person("childcare_hours_per_day", period.this_year)
        return hours_per_day >= p.full_time_hours_per_day
