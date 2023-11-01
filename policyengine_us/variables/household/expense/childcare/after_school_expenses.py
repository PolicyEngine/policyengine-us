from policyengine_us.model_api import *


class after_school_expenses(Variable):
    value_type = float
    entity = Person
    label = "After school childcare expenses"
    definition_period = YEAR
    unit = USD
