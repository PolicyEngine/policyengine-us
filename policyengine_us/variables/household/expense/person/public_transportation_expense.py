from policyengine_us.model_api import *


class public_transportation_expense(Variable):
    value_type = float
    entity = Person
    label = "Public transportation expense"
    unit = USD
    definition_period = YEAR
