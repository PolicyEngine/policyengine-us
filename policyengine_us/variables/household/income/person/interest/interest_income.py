from policyengine_us.model_api import *


class interest_income(Variable):
    value_type = float
    entity = Person
    label = "Interest income"
    unit = USD
    definition_period = YEAR

    formula = sum_of_variables(
        ["taxable_interest_income", "tax_exempt_interest_income"]
    )
