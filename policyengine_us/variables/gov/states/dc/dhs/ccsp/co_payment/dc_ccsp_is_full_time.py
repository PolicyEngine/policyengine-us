from policyengine_us.model_api import *


class dc_ccsp_is_full_time(Variable):
    value_type = bool
    entity = Person
    label = "Person is attending full time day care under DC Child Care Subsidy Program (CCSP)"
    definition_period = MONTH
    defined_for = StateCode.DC

    def formula(person, period, parameters):
        schedule_type = person("dc_ccsp_schedule_type", period)
        full_time_traditional = (
            schedule_type
            == schedule_type.possible_values.FULL_TIME_TRADITIONAL
        )
        full_time_extended_day = (
            schedule_type
            == schedule_type.possible_values.EXTENDED_DAY_FULL_TIME
        )
        full_time_nontraditional = (
            schedule_type
            == schedule_type.possible_values.FULL_TIME_NONTRADITIONAL
        )
        return (
            full_time_traditional
            | full_time_extended_day
            | full_time_nontraditional
        )
