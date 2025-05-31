from policyengine_us.model_api import *


class fuel_oil_expense(Variable):
    value_type = float
    entity = SPMUnit
    label = "Fuel oil expense"
    unit = USD
    definition_period = YEAR
