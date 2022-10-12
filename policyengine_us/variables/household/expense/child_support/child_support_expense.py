from policyengine_us.model_api import *


class child_support_expense(Variable):
    value_type = float
    entity = Person
    label = "Child support expense"
    unit = USD
    documentation = "Legally mandated child support expenses."
    definition_period = YEAR
