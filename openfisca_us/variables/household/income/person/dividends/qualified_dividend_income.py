from policyengine_us.model_api import *


class qualified_dividend_income(Variable):
    value_type = float
    entity = Person
    label = "Qualified dividend income"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        qualified_percentage = parameters(
            period
        ).calibration.programs.income.dividends.qualified_percentage
        total_dividends = person("dividend_income", period)
        return total_dividends * qualified_percentage
