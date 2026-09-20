from policyengine_us.model_api import *


class sc_ccap_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for South Carolina CCAP based on activity requirements"
    definition_period = MONTH
    defined_for = StateCode.SC
    reference = (
        "https://www.scchildcare.org/media/ubhdm1at/1-13-2025_policy-manual.pdf#page=22"
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.sc.dss.ccap.eligibility
        person = spm_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        hours_worked = person("weekly_hours_worked", period.this_year)
        meets_work_requirement = hours_worked >= p.activity_hours
        is_student = person("is_full_time_student", period.this_year)
        # Per Section 2.13, a disabled parent satisfies the activity
        # requirement (one parent working/school + other disabled,
        # or both parents disabled).
        is_disabled = person("is_disabled", period.this_year)
        individually_eligible = meets_work_requirement | is_student | is_disabled
        # Require at least one head/spouse in the unit so an SPM unit
        # containing only dependents does not vacuously pass the test,
        # and require every head/spouse present to be individually
        # eligible. Mirrors the VA CCSP activity-test pattern.
        has_head_or_spouse = spm_unit.sum(is_head_or_spouse) >= 1
        all_covered = spm_unit.sum(is_head_or_spouse & ~individually_eligible) == 0
        has_court_child = spm_unit.any(
            person("sc_ccap_eligible_child", period)
            & person("is_under_court_supervision", period.this_year)
        )
        court_waiver = has_court_child & spm_unit(
            "sc_ccap_court_care_activity_waived", period
        )
        return (has_head_or_spouse & all_covered) | court_waiver
