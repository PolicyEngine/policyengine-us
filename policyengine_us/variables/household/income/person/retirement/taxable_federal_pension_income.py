from policyengine_us.model_api import *


class taxable_federal_pension_income(Variable):
    value_type = float
    entity = Person
    label = "Taxable federal pension income"
    unit = USD
    definition_period = YEAR
