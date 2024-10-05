from policyengine_us.model_api import *


class assessed_property_value(Variable):
    value_type = float
    entity = Person
    label = "Assessed property value"
    unit = USD
    documentation = "Total assessed value of property owned by this person."
    definition_period = YEAR
