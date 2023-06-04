from policyengine_us.model_api import *


class va_tanf_gross_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "VA TANF gross earned income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.VA

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        person_earned_income = person("earned_income", period)
        child_0_17 = person("is_child", period)
        full_time_student = person("is_full_time_student", period)
        nonchild_earned_income = where(
            child_0_17 & full_time_student, 0, person_earned_income
        )

        return spm_unit.sum(nonchild_earned_income)
