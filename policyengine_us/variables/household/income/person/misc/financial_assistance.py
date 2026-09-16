from policyengine_us.model_api import *


class financial_assistance(Variable):
    value_type = float
    entity = Person
    label = "financial assistance"
    documentation = (
        "Cash financial assistance from friends or relatives outside the household."
    )
    unit = USD
    definition_period = YEAR
