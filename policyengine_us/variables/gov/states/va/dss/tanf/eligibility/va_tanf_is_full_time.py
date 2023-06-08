from policyengine_us.model_api import *


class va_tanf_is_full_time(Variable):
    value_type = bool
    entity = SPMUnit
    label = "VA TANF care expenses"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.VA

    def formula(spm_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.va.dss.tanf.income.deduction.full_time_work_hours
        person = spm_unit.members
        person_work_hour = person("work_hours_per_week", period)
        child = person("is_child", period)
        return spm_unit.any((person_work_hour >= p) & (~child))
