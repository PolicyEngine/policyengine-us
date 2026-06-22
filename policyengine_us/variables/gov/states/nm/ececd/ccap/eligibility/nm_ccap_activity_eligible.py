from policyengine_us.model_api import *


class nm_ccap_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for New Mexico CCAP based on activity requirements"
    definition_period = MONTH
    defined_for = StateCode.NM
    reference = "https://www.srca.nm.gov/parts/title08/08.015.0002.html"

    def formula(spm_unit, period, parameters):
        # 8.15.2.11.I / 8.15.2.7: benefits are for families working, attending
        # school, or in job training. 8.15.2.11.I requires the activity to be
        # present (it does not set a minimum-hours floor), so we test for any
        # work hours or full-time student status. Each head/spouse caretaker
        # must independently meet the activity requirement. We don't track
        # job-training participation or temporary activity interruptions
        # (8.15.2.7) at the moment.
        person = spm_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        hours_worked = person("weekly_hours_worked", period.this_year)
        is_student = person("is_full_time_student", period.this_year)
        individually_eligible = (hours_worked > 0) | is_student
        has_caretaker = spm_unit.sum(is_head_or_spouse) > 0
        no_ineligible_caretaker = (
            spm_unit.sum(is_head_or_spouse & ~individually_eligible) == 0
        )
        return has_caretaker & no_ineligible_caretaker
