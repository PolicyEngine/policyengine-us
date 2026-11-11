from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.co.ccap.co_ccap_child_in_part_time_care import (
    FIRST_GRADE_AGE,
)


class co_ccap_after_school_care_only(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Colorado Child Care Assistance Program child in grade 1 or above whose only reported care comes after school"
    documentation = (
        "A child in grade 1 or above with no hours or days of care whose only "
        "care expense is after school. After-school care fills part of a school "
        "day, and the child has it in most months (section 3.124(V)), so the "
        "parent fee and the county rate both read it as part-time care."
    )
    defined_for = StateCode.CO
    reference = (
        # 8 CCR 1403-1 3.124(V) and (W), PDF page 85.
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=12658&fileName=8%20CCR%201403-1#page=85",
    )

    def formula(person, period, parameters):
        year = period.this_year
        in_grade_one_or_above = person("is_in_k12_school", year) & (
            person("age", year) >= FIRST_GRADE_AGE
        )
        no_schedule = (
            (person("co_ccap_care_hours_per_day", period) == 0)
            & (person("childcare_days_per_week", year) == 0)
            & (person("childcare_attending_days_per_month", year) == 0)
        )
        after_school_only = (person("after_school_expenses", year) > 0) & (
            person("pre_subsidy_childcare_expenses", year) == 0
        )
        return in_grade_one_or_above & no_schedule & after_school_only
