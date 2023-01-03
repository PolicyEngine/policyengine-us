from policyengine_us.model_api import *


class public_pension_income(Variable):
    value_type = float
    entity = Person
    label = "Public pension income"
    unit = USD
    documentation = "Income from government employee pensions."
    definition_period = YEAR
