from policyengine_us.model_api import *


class general_assistance(Variable):
    value_type = float
    entity = Person
    label = "general assistance"
    unit = USD
    definition_period = YEAR
