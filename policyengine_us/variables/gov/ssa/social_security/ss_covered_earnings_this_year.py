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
        # For now, this is a simplified version
        # In reality, this would be capped at the Social Security wage base
        employment_income = person("employment_income", period)
        self_employment_income = person("self_employment_income", period)

        # TODO: Apply Social Security wage base cap
        # TODO: Exclude certain types of income

        return employment_income + self_employment_income

