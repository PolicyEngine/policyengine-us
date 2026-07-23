from policyengine_us.model_api import *


class or_erdc_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Eligible for Oregon ERDC based on caretaker activity"
    defined_for = StateCode.OR
    reference = (
        "https://secure.sos.state.or.us/oard/view.action?ruleNumber=414-175-0023"
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states["or"].delc.erdc
        categorical = spm_unit("or_erdc_categorically_eligible", period)
        person = spm_unit.members
        caretaker = person("is_tax_unit_head_or_spouse", period.this_year)
        caretaker_count = spm_unit.sum(caretaker)
        working = person("weekly_hours_worked_before_lsr", period.this_year) > 0
        postsecondary_student = person(
            "is_full_time_college_student", period.this_year
        ) | person("is_part_time_college_student", period.this_year)
        education_age_eligible = (
            person("age", period.this_year) <= p.age_threshold.education
        )
        # OAR 414-175-0023(1)(a)(B) covers secondary school, GED, and
        # equivalent training, which is_in_secondary_school includes; medical
        # leave under (1)(a)(C) is not tracked at the moment.
        secondary_student = (
            person("is_in_secondary_school", period.this_year) & education_age_eligible
        )
        # OAR 414-175-0023(1)(b)(A) excuses a second caretaker who is
        # physically or mentally unable to provide adequate care, proxied by
        # disability status; the supervised-contact exception in (1)(b)(B)
        # is not tracked at the moment.
        unable_to_care = person("is_disabled", period.this_year)
        multiple_caretakers = spm_unit.project(caretaker_count > 1)
        caretaker_eligible = (
            working
            | postsecondary_student
            | secondary_student
            | (multiple_caretakers & unable_to_care)
        )
        has_caretaker = caretaker_count > 0
        all_caretakers_eligible = spm_unit.sum(caretaker & ~caretaker_eligible) == 0
        return categorical | (has_caretaker & all_caretakers_eligible)
