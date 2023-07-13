from policyengine_us.model_api import *


class mi_heating_cost(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan household heating cost"
    defined_for = StateCode.MI
    unit = USD
    definition_period = YEAR
