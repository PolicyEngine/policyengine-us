from policyengine_us.model_api import *


class ny_ccap_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for New York CCAP based on the reason for care"
    definition_period = MONTH
    defined_for = StateCode.NY
    documentation = (
        "18 NYCRR 415.2(a)(2)(v)(a) serves a family whose caretakers are "
        "engaged in work, and the section's opening paragraph requires each "
        "caretaker of a two-caretaker family to meet one of the criteria. "
        "415.1(o)(1)(i) defines engaged in work by a minimum weekly hours "
        "figure the Office sets outside Part 415, so any hours count here. "
        "Educational and vocational activities under 415.2(a)(2)(v)(d) are "
        "read from full-time student status, and 415.2(a)(1)(i) and (iii) "
        "guarantee care to a public assistance family whose caretaker is in "
        "a required work activity; is_tanf_enrolled stands in for that "
        "required-activity condition. The remaining pathways — job search, the "
        "individual training programs, domestic violence services, substance "
        "abuse treatment, and a caretaker who is incapacitated or has family "
        "duties away from home — are represented by the "
        "meets_ccdf_activity_test input."
    )
    reference = "https://ocfs.ny.gov/programs/childcare/regulations/415-Child-Care-Services.pdf#page=13"

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        is_caretaker = person("is_tax_unit_head_or_spouse", period.this_year)
        hours = person("weekly_hours_worked_before_lsr", period.this_year)
        in_activity = (hours > 0) | person("is_full_time_student", period.this_year)
        has_caretaker = spm_unit.sum(is_caretaker) > 0
        every_caretaker_active = spm_unit.sum(is_caretaker & ~in_activity) == 0
        work_eligible = has_caretaker & every_caretaker_active
        # is_tanf_enrolled reflects reported enrollment rather than the
        # computed tanf amount, so reading it does not close the
        # CCAP -> TANF -> child care expenses circular dependency.
        public_assistance = spm_unit("is_tanf_enrolled", period)
        fallback = spm_unit("meets_ccdf_activity_test", period.this_year)
        return work_eligible | public_assistance | fallback
