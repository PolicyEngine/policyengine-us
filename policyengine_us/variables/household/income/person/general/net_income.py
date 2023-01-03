from policyengine_us.model_api import *


class net_income(Variable):
    value_type = float
    entity = Person
    label = "Net income"
    unit = USD
    documentation = "Personal disposable income after taxes and transfers"
    definition_period = YEAR
