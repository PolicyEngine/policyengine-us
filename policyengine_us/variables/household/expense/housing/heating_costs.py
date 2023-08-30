from policyengine_us.model_api import *


class heating_costs(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan household heating cost"
    unit = USD
    definition_period = YEAR
    
