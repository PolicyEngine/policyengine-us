from policyengine_us.model_api import *


class va_tanf_care_expenses(Variable):
    value_type = float
    entity = SPMUnit
    label = "VA TANF care expenses"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.VA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.va.dss.tanf.income.deduction
        is_full_time = spm_unit("va_tanf_is_full_time", period)
        person = spm_unit.members
        child = person("is_child", period)
        age = person("age", period)
        adult = person("is_adult", period)
        disabled = person("is_disabled", period)
        disabled_adult = adult & disabled
        care_recipient = child | disabled_adult

        full_time_care_expenses = spm_unit.sum(
            p.care_expenses_full_time.calc(age) * care_recipient
        )
        part_time_care_expenses = spm_unit.sum(
            p.care_expenses_part_time * care_recipient
        )
        monthly_care_expenses = where(
            is_full_time, full_time_care_expenses, part_time_care_expenses
        )

        return monthly_care_expenses * MONTHS_IN_YEAR
