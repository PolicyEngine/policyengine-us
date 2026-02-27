from policyengine_us.model_api import *


class ss_covered_earnings_this_year(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Social Security covered earnings this year"
    documentation = (
        "Earnings subject to Social Security tax for the current year"
    )
    unit = USD

    def formula(person, period, parameters):
        employment_income = person("employment_income", period)
        self_employment_income = person("self_employment_income", period)

        total_earnings = employment_income + self_employment_income

        # Apply Social Security wage base cap
        p = parameters(period).gov.ssa.social_security
        wage_base = p.wage_base

        return min_(total_earnings, wage_base)
