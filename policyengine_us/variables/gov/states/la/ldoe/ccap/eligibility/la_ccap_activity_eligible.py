from policyengine_us.model_api import *


class la_ccap_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Louisiana CCAP activity eligible"
    reference = "https://www.doa.la.gov/media/043btqeh/28v165.docx"
    defined_for = StateCode.LA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.la.ldoe.ccap
        person = spm_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        hours = person("weekly_hours_worked_before_lsr", period.this_year)
        student = person("is_full_time_student", period.this_year)
        disabled = person("is_disabled", period.this_year)
        age = person("age", period.this_year)
        # LAC 28:CLXV.509.A.5.d reduces the hours requirement for households
        # that qualify for special needs child care.
        has_special_needs_child = spm_unit.any(
            disabled & (age < p.age.disabled_child_limit)
        )
        required_hours = where(
            has_special_needs_child,
            p.activity.special_needs_weekly_hours,
            p.activity.weekly_hours,
        )
        # LAC 28:CLXV.509.A.5.a: 20 hours per week of employment, training, or
        # education, or full-time student status; waived for disabled adults
        # (§509.A.5.a) — each adult must meet the requirement per the TEMP
        # definition in §103. The 90-day job-search waiver is a time-limited
        # certification state we don't model.
        meets = (hours >= spm_unit.project(required_hours)) | student | disabled
        failing_adults = spm_unit.sum(is_head_or_spouse & ~meets)
        # §509.A.5.b waives the requirement for homeless parents.
        homeless = spm_unit.household("is_homeless", period.this_year)
        return (failing_adults == 0) | homeless
