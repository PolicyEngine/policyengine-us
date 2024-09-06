from policyengine_us.model_api import *


class military_retirement_pay_survivors(Variable):
    value_type = float
    entity = Person
    label = "Military retirement income paid to surviving spouses"
    unit = USD
    definition_period = YEAR
