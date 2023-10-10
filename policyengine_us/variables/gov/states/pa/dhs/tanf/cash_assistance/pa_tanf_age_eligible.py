from policyengine_us.model_api import *


class pa_tanf_age_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Pennsylvania TANF age eligibility"
    definition_period = YEAR
    defined_for = StateCode.PA

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        p = parameters(period).gov.states.pa.dhs.tanf.cash_assistance
        age = person("age", period)
        # Get full time students
        student_eligible = person("is_full_time_student", period) & (
            age == p.age_limit
        )

        # Get age
        is_eligible_age = age < p.age_limit
        return spm_unit.any(is_eligible_age | student_eligible)
