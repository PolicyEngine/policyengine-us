from policyengine_us.model_api import *


class rent(Variable):
    value_type = float
    entity = Person
    label = "Rent"
    unit = USD
    definition_period = YEAR
