from policyengine_us.model_api import *


class dc_ccsp_qualified_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for DC Child Care Subsidy Program (CCSP) due to qualified activity"
    definition_period = MONTH
    defined_for = StateCode.DC
    reference = "https://osse.dc.gov/sites/default/files/dc/sites/osse/publication/attachments/DC%20Child%20Care%20Subsidy%20Program%20Policy%20Manual.pdf#page=8"

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
