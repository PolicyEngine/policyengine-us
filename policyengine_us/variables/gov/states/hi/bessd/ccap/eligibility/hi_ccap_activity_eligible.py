from policyengine_us.model_api import *


class hi_ccap_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Hawaii CCAP based on caretaker activity"
    definition_period = MONTH
    defined_for = StateCode.HI
    reference = "https://humanservices.hawaii.gov/bessd/files/2013/01/HAR-17-798.2-Child-Care-Services-Rules.pdf#page=15"

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        # Approved activities (HAR 17-798.2-9(b)(2)). We model the core work,
        # education/training, and protective-services pathways. Activity
        # pathways for short-term job offers, employment breaks, job search,
        # first-to-work, and protective-order day care rely on timing windows
        # we don't track at the moment. Use the pre-labor-supply-response work
        # hours to avoid a circular dependency with behavioral responses.
        is_employed = (
            person("weekly_hours_worked_before_lsr", period.this_year) > 0
        ) | (person("employment_income", period.this_year) > 0)
        is_student = person("is_full_time_student", period.this_year)
        protective_services = person(
            "receives_or_needs_protective_services", period.this_year
        )
        real_activity = is_employed | is_student | protective_services
        # Disability is NOT a standalone activity: under HAR 17-798.2-9(b)(2)(H)
        # and (I), an incapacitated caretaker qualifies the family only via an
        # activity link -- when the OTHER head/spouse is in an approved
        # activity. A single idle disabled caretaker, or two idle disabled
        # parents, do not qualify.
        is_disabled = person("is_disabled", period.this_year)
        is_caretaker = is_head_or_spouse
        # A caretaker who is neither in a real activity nor disabled disqualifies
        # the unit outright.
        n_inactive_nondisabled = spm_unit.sum(
            is_caretaker & ~real_activity & ~is_disabled
        )
        # A disabled, non-active caretaker is covered only if another caretaker
        # is in a real activity.
        n_disabled_inactive = spm_unit.sum(is_caretaker & ~real_activity & is_disabled)
        n_real_active = spm_unit.sum(is_caretaker & real_activity)
        return (n_inactive_nondisabled == 0) & (
            (n_disabled_inactive == 0) | (n_real_active >= 1)
        )
