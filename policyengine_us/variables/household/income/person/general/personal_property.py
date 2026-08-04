from policyengine_us.model_api import *


class personal_property(Variable):
    value_type = float
    entity = Person
    label = "Personal property value"
    unit = USD
    quantity_type = STOCK
    definition_period = YEAR
