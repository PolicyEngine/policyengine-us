from policyengine_us.model_api import *


class financial_assistance(Variable):
    value_type = float
    entity = Person
    label = "financial assistance"
    documentation = "Cash financial assistance from outside the household."
    unit = USD
    definition_period = YEAR
