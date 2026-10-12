from policyengine_us.model_api import *


class al_ccsp_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Alabama CCSP based on parental activity requirements"
    definition_period = MONTH
    defined_for = StateCode.AL
    reference = "https://dhr.alabama.gov/wp-content/uploads/2023/04/2025-2027-CCDF-State-Plan-with-Approval-Letter.pdf#page=22"

    def formula(spm_unit, period, parameters):
        # Alabama §2.2.2(d)(ii) applies the activity test to the parent(s)
        # or in loco parentis caregiver(s). We approximate the caregiver
        # set with is_tax_unit_head_or_spouse; grandparent / kinship /
        # foster caregivers who aren't the tax-unit head won't be checked
        # individually, so users should set meets_ccdf_activity_test in
        # those cases.
        p = parameters(period).gov.states.al.dhr.ccsp.activity
        person = spm_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        hours_worked = person("weekly_hours_worked", period.this_year)
        meets_work_requirement = hours_worked >= p.hours_minimum
        is_student = person("is_full_time_student", period.this_year)
        individually_eligible = meets_work_requirement | is_student
        has_head_or_spouse = spm_unit.sum(is_head_or_spouse) >= 1
        all_covered = spm_unit.sum(is_head_or_spouse & ~individually_eligible) == 0
        # Permissive fallback for approved activities not individually
        # modeled (job search, education/training, SNAP E&T, temporary
        # leave, disabled-parent good cause, in loco parentis caregivers,
        # etc.). §2.2.2 only waives the activity test categorically for
        # children receiving protective services (§2.2.2(h)); other
        # exemptions must be set via this fallback input.
        fallback = spm_unit("meets_ccdf_activity_test", period.this_year)
        return (has_head_or_spouse & all_covered) | fallback
