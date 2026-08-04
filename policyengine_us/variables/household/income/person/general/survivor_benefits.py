from policyengine_us.model_api import *


class survivor_benefits(Variable):
    value_type = float
    entity = Person
    label = "survivor benefits"
    documentation = "Survivor benefits other than Social Security survivor benefits."
    unit = USD
    definition_period = YEAR
