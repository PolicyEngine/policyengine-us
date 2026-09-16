from policyengine_us.model_api import *


class other_heating_fuel_expense(Variable):
    value_type = float
    entity = SPMUnit
    label = "Other heating fuel expense"
    unit = USD
    definition_period = YEAR
    documentation = "Annual expense for a heating fuel with no dedicated expense input; pairs with the OTHER heating type."
