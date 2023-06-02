from policyengine_us.model_api import *


class heating_cost(Variable):
    value_type = float
    entity = TaxUnit
    label = "Household heating cost"
    defined_for = StateCode.MI
    unit = USD
    definition_period = YEAR
