from policyengine_us.model_api import *


class childcare_expenses_per_child(Variable):
    value_type = float
    entity = Person
    label = "Monthly child care expenses for each individual child"
    unit = USD
    definition_period = MONTH
