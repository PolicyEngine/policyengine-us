from policyengine_us.model_api import *


class il_ccap_parent_meets_working_requirements(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Parent meets Illinois Child Care Assistance Program (CCAP) working requirements"
    definition_period = MONTH
    defined_for = StateCode.IL
    reference = "https://www.dhs.state.il.us/page.aspx?item=104995"

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        is_working = (
            add(
                person,
                period,
                ["employment_income", "self_employment_income"],
            )
            > 0
        )
        is_full_time_student = person("is_full_time_student", period)
        ineligible_parent = head_or_spouse & ~(
            is_working | is_full_time_student
        )
        return spm_unit.sum(ineligible_parent) == 0
