from openfisca_us.model_api import *


class ordinary_dividend_income(Variable):
    value_type = float
    entity = Person
    label = "Ordinary dividend income"
    unit = USD
    definition_period = YEAR

    formula = sum_of_variables(
        ["qualified_dividend_income", "non_qualified_dividend_income"]
    )
