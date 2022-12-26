from policyengine_us.model_api import *


class household_market_income(Variable):
    value_type = float
    entity = Household
    label = "market income"
    documentation = "Income from non-government sources."
    definition_period = YEAR
    unit = USD
    adds = [
        "employment_income",
        "self_employment_income",
        "pension_income",
        "dividend_income",
        "interest_income",
        "gi_cash_assistance",
        "capital_gains",
        "rental_income",
        "illicit_income",
        "farm_income",
    ]
