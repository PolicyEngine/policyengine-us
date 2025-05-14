from policyengine_us.model_api import *


class overtime_income(Variable):
    value_type = float
    entity = Person
    label = "Income from overtime hours worked"
    unit = USD
    definition_period = YEAR

    # This variable only exists for the purpose of the tax_exempt_reform
