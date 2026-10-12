from policyengine_us.model_api import *


class oh_ccap_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Ohio CCAP based on qualifying activity"
    definition_period = MONTH
    defined_for = StateCode.OH
    reference = "https://codes.ohio.gov/ohio-administrative-code/rule-5180:6-1-02"

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        is_caretaker = person("is_tax_unit_head_or_spouse", period.this_year)
        is_active = (person("weekly_hours_worked", period.this_year) > 0) | person(
            "is_full_time_student", period.this_year
        )
        has_caretaker = spm_unit.sum(is_caretaker) > 0
        all_caretakers_active = spm_unit.sum(is_caretaker & ~is_active) == 0
        return (has_caretaker & all_caretakers_active) | spm_unit(
            "meets_ccdf_activity_test", period.this_year
        )
