from policyengine_us.model_api import *


class co_ccap_child_in_care(Variable):
    value_type = bool
    entity = Person
    label = "Child in care under the Colorado Child Care Assistance Program"
    documentation = (
        "An eligible child for whom the household requests care. Reported care "
        "hours or days show care, and so does a child care or after-school "
        "expense, since surveys ask what families pay for care but not when "
        "the care happens."
    )
    reference = (
        # PDF pages 79, 84
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=12658&fileName=8%20CCR%201403-1#page=79",
    )
    definition_period = MONTH
    defined_for = StateCode.CO

    def formula(person, period, parameters):
        year = period.this_year
        eligible = person("co_ccap_child_eligible", period)
        has_schedule = (
            (person("childcare_hours_per_day", year) > 0)
            | (person("childcare_hours_per_week", year) > 0)
            | (person("childcare_days_per_week", year) > 0)
            | (person("childcare_attending_days_per_month", year) > 0)
        )
        expenses = add(
            person,
            year,
            ["pre_subsidy_childcare_expenses", "after_school_expenses"],
        )
        return eligible & (has_schedule | (expenses > 0))
