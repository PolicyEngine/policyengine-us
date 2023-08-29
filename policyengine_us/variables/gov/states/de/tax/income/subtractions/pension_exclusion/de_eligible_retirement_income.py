from policyengine_us.model_api import *


class de_eligible_retirement_income_for_elderly(Variable):
    value_type = float
    entity = Person
    label = "Delaware eligible retirement income amount for elderly"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DE

    def formula(tax_unit, period, parameters):
        adds = [
            "dividend_income",
            "capital_gains",
            "taxable_interest_income",
            "rental_income",
        ]
