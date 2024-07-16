from policyengine_us.model_api import *


class head_start(Variable):
    value_type = float
    entity = Person
    label = "Head Start value"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://eclkc.ohs.acf.hhs.gov/policy/45-cfr-chap-xiii/1302-12-determining-verifying-documenting-eligibility"
        "https://www.hhs.gov/answers/programs-for-families-and-children/how-can-i-get-my-child-into-head-start/index.html"
    )
    defined_for = "is_head_start_eligible"

    def formula(person, period, parameters):
        p = parameters(period).gov.hhs.head_start
        childcare_expenses = person("pre_subsidy_childcare_expenses", period)
        childcare_hours = (
            person("childcare_hours_per_week", period) * WEEKS_IN_YEAR
        )
        return childcare_expenses * (p.minimum_hours / childcare_hours)
