from openfisca_us.model_api import *


class non_qualified_dividend_income(Variable):
    value_type = float
    entity = Person
    label = "Ordinary dividend income"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        total_dividends = person("dividend_income", period)
        qualified_dividends = person("qualified_dividend_income", period)
        return total_dividends - qualified_dividends
