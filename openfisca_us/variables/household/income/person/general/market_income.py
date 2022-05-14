from openfisca_us.model_api import *


class market_income(Variable):
    value_type = float
    entity = Person
    label = "Market income"
    unit = USD
    documentation = "Income from all non-government sources"
    definition_period = YEAR

    def formula(person, period, parameters):
        COMPONENTS = [
            "employment_income",
            "self_employment_income",
            "pension_income",
            "dividend_income",
            "interest_income",
            "gi_cash_assistance",
        ]
        return add(person, period, COMPONENTS)
