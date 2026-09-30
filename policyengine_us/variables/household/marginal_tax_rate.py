from policyengine_us.model_api import *
from policyengine_us.variables.household.marginal_tax_rate_helpers import (
    marginal_earnings_change,
)


class marginal_tax_rate(Variable):
    label = "marginal tax rate"
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
            lambda population: population.household("household_net_income", period),
            "mtr",
        )
        return where(measured, 1 - increase, 0)


class adult_index(Variable):
    value_type = int
    entity = Person
    label = "Index of adult in household"
    definition_period = YEAR

    def formula(person, period, parameters):
        return (
            person.get_rank(
                person.household,
                -person("age", period),
                condition=person("is_adult", period),
            )
            + 1
        )


class adult_earnings_index(Variable):
    value_type = int
    entity = Person
    label = "index of adult in household by earnings"
    definition_period = YEAR

    def formula(person, period, parameters):
        return (
            person.get_rank(
                person.household,
                -person("market_income", period),
                condition=person("is_adult", period),
            )
            + 1
        )
