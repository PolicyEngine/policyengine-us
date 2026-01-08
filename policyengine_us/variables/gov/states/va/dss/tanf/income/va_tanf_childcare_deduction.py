from policyengine_us.model_api import *


class va_tanf_childcare_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "VA TANF childcare deduction"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.VA
    reference = "https://www.dss.virginia.gov/files/division/bp/tanf/manual/300_11-20.pdf#page=56"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.va.dss.tanf.income.deduction
        is_full_time = spm_unit("va_tanf_is_full_time", period)
        person = spm_unit.members
        child = person("is_child", period)
        age = person("age", period.this_year)
        adult = person("is_adult", period)
        disabled = person("is_disabled", period)
        disabled_adult = (adult) & (disabled)
        care_recipient = (child) | (disabled_adult)

        full_time_care_expenses = spm_unit.sum(
            p.care_expenses_full_time.calc(age) * care_recipient
        )
        part_time_care_expenses = spm_unit.sum(
            p.care_expenses_part_time * care_recipient
        )

        return where(
            is_full_time, full_time_care_expenses, part_time_care_expenses
        )
