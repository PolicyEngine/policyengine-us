from policyengine_us.model_api import *


class military_basic_pay(Variable):
    value_type = float
    entity = Person
    label = "Military basic pay"
    unit = USD
    definition_period = YEAR
