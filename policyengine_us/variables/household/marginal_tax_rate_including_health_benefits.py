from policyengine_us.model_api import *
from policyengine_us.variables.household.marginal_tax_rate_helpers import (
    marginal_earnings_change,
)


class marginal_tax_rate_including_health_benefits(Variable):
    label = "Marginal tax rate including health benefits"
    documentation = (
        "Fraction of marginal income gains that do not increase household net income."
    )
    entity = Person
    definition_period = YEAR
    value_type = float
    unit = "/1"

    def formula(person, period, parameters):
        increase, measured = marginal_earnings_change(
            person,
            period,
            parameters,
            lambda population: population.household(
                "household_net_income_including_health_benefits", period
            ),
            "mtr_including_health_benefits",
        )
        return where(measured, 1 - increase, 0)
