from policyengine_us.model_api import *


class tx_ccs_work_requirement_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Texas CCS work requirement eligible"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/texas/40-Tex-Admin-Code-SS-809-56"
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.tx.twc.ccs.work_requirements

        # Get work hours for tax unit heads and spouses in the SPM unit
        person = spm_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        work_hours = person("weekly_hours_worked", period.this_year)
        parent_work_hours = where(is_head_or_spouse, work_hours, 0)
        # Sum total work hours
        total_work_hours = spm_unit.sum(parent_work_hours)
        # Check requirements based on number of parents
        is_two_parent_unit = spm_unit.sum(is_head_or_spouse) > 1
        single_parent_requirement = total_work_hours >= p.single_parent
        two_parent_requirement = total_work_hours >= p.two_parent
        is_working = where(
            is_two_parent_unit,
            two_parent_requirement,
            single_parent_requirement,
        )
        # Enroll in education program satisfied work requirement
        is_full_time_student = person("is_full_time_student", period)

        meets_work_requirements = (
            is_working | is_full_time_student | ~is_head_or_spouse
        )
        return spm_unit.sum(~meets_work_requirements) == 0
