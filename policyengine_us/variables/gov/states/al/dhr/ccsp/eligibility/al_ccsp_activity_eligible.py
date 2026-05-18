from policyengine_us.model_api import *


class al_ccsp_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Alabama CCSP based on parental activity requirements"
    documentation = (
        "True when every head/spouse in the SPM unit meets §2.2.2 work or "
        "full-time-student requirements, OR when meets_ccdf_activity_test "
        "is set as an input override. The fallback is permissive: a unit "
        "with one working and one non-working parent (which §2.2.2 would "
        "deny) is treated as eligible when meets_ccdf_activity_test is True. "
        "Users who need strict §2.2.2 enforcement should leave the override "
        "unset."
    )
    definition_period = MONTH
    defined_for = StateCode.AL
    reference = (
        "Alabama CCDF State Plan 2025-2027, Section 2.2.2",
        "https://dhr.alabama.gov/wp-content/uploads/2023/04/2025-2027-CCDF-State-Plan-with-Approval-Letter.pdf#page=21",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.al.dhr.ccsp.activity
        person = spm_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        hours_worked = person("weekly_hours_worked", period.this_year)
        meets_work_requirement = hours_worked >= p.hours_minimum
        is_student = person("is_full_time_student", period.this_year)
        individually_eligible = meets_work_requirement | is_student
        has_head_or_spouse = spm_unit.sum(is_head_or_spouse) >= 1
        all_covered = spm_unit.sum(is_head_or_spouse & ~individually_eligible) == 0
        # Fallback input for approved activities not individually modeled
        # (job search, education/training, SNAP E&T, temporary leave,
        # disabled-parent good cause, etc.). Alabama's §2.2.2 only waives
        # the activity test for children receiving protective services
        # (§2.2.2(h)); other exemptions must be set via this fallback.
        fallback = spm_unit("meets_ccdf_activity_test", period.this_year)
        return (has_head_or_spouse & all_covered) | fallback
