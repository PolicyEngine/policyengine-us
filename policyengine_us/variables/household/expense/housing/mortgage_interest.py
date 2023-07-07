from policyengine_us.model_api import *


class mortgage_interest(Variable):
    value_type = float
    entity = Person
    label = "mortgage interest"
    unit = USD
    definition_period = YEAR
