from policyengine_us.model_api import *


class ia_tanf_fip_has_eligible_child(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Iowa FIP has eligible child"
    definition_period = MONTH
    reference = "Iowa Code Chapter 239B.2"
    documentation = (
        "FIP requires responsibility for a child under age 18, or age 19 "
        "if still in high school."
    )
    defined_for = StateCode.IA

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        age = person("age", period.this_year)

        # Child is under 18
        has_child_under_18 = spm_unit.any(age < 18)

        # Or age 18 and in high school (we'll use is_student as proxy)
        is_18 = age == 18
        is_student = person("is_full_time_student", period)
        has_18_year_old_student = spm_unit.any(is_18 & is_student)

        return has_child_under_18 | has_18_year_old_student
