from policyengine_us.model_api import *


class wv_ccap_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for West Virginia CCAP based on activity requirements"
    definition_period = MONTH
    defined_for = StateCode.WV
    reference = "https://bfa.wv.gov/media/6766/download?inline#page=32"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.wv.dhhr.ccap.eligibility
        person = spm_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        hours_worked = person("weekly_hours_worked", period.this_year)
        meets_work_requirement = hours_worked >= p.activity_hours
        is_student = person("is_full_time_student", period.this_year)
        individually_eligible = meets_work_requirement | is_student
        # A unit with no head or spouse (e.g., a child-only record) has no
        # caretaker to be in a qualifying activity and must not pass.
        has_caretaker = spm_unit.sum(is_head_or_spouse) > 0
        no_ineligible_caretaker = (
            spm_unit.sum(is_head_or_spouse & ~individually_eligible) == 0
        )
        return has_caretaker & no_ineligible_caretaker
