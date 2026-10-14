from policyengine_us.model_api import *


class total_charitable_donations(Variable):
    value_type = float
    entity = Person
    label = "Total charitable donations"
    unit = USD
    definition_period = YEAR
    documentation = "Gross total charitable donations across all categories."

    def formula(person, period, parameters):
        return (
            person("charitable_cash_donations_50_pct", period)
            + person("charitable_cash_donations_non_50_pct", period)
            + person("charitable_non_cash_donations_50_pct", period)
            + person("charitable_non_cash_donations_non_50_pct", period)
            + person("charitable_capital_gain_donations_50_pct", period)
            + person("charitable_capital_gain_donations_non_50_pct", period)
        )
