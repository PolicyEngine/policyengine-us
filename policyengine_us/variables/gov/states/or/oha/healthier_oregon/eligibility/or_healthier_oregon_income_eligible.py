from policyengine_us.model_api import *


class or_healthier_oregon_income_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Meets Oregon Healthier Oregon income eligibility"
    definition_period = YEAR
    defined_for = StateCode.OR
    reference = (
        "https://www.oregon.gov/oha/hsd/ohp/pages/healthier-oregon.aspx",
        "https://www.opb.org/article/2023/07/10/oregon-expands-health-coverage-low-income-residents-immigrants/",
    )

    def formula(person, period, parameters):
        p = (
            parameters(period)
            .gov.states["or"]
            .oha.healthier_oregon.eligibility
        )
        income_level = person("medicaid_income_level", period)

        age = person("age", period)
        is_child = age < p.child_max_age

        # Different income limits based on age
        income_limit = where(
            is_child,
            p.child_income_limit,
            p.adult_income_limit,
        )

        return income_level <= income_limit
