from policyengine_us.model_api import *


class salt_refund_income(Variable):
    value_type = float
    entity = Person
    label = "State and local tax refund income"
    unit = USD
    definition_period = YEAR
