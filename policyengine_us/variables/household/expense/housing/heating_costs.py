from policyengine_us.model_api import *


class heating_costs(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax unit heating cost"
    unit = USD
    definition_period = YEAR
