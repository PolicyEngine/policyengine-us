from policyengine_us.model_api import *


class wv_ccap_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for West Virginia CCAP based on activity requirements"
    definition_period = MONTH
    defined_for = StateCode.WV
    reference = "https://bfa.wv.gov/media/6766/download?inline#page=33"

    def formula(spm_unit, period, parameters):
        # NOTE: we use is_full_time_student as a proxy for Manual §3.6.3, which
        # requires specific credit-hour minimums and excludes web-only courses.
        # We don't track high-school students (§3.6.2.2 exempts them from the
        # weekly-hours floor) or CPS Safety/Treatment Plan recipients
        # (§3.6.4 exempts them from activity hours) at the moment.
        p = parameters(period).gov.states.wv.dhhr.ccap.eligibility
        person = spm_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        hours_worked = person("weekly_hours_worked", period.this_year)
        is_student = person("is_full_time_student", period.this_year)
        individually_eligible = (hours_worked >= p.activity_hours) | is_student
        has_caretaker = spm_unit.sum(is_head_or_spouse) > 0
        no_ineligible_caretaker = (
            spm_unit.sum(is_head_or_spouse & ~individually_eligible) == 0
        )
        return has_caretaker & no_ineligible_caretaker
