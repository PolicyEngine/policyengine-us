from policyengine_us.model_api import *


class taxable_estate_value(Variable):
    value_type = float
    entity = Person
    label = "Taxable estate taxes"
    unit = USD
    definition_period = YEAR
