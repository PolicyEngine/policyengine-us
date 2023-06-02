from policyengine_us.model_api import *

class rent_include_heating_cost(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Rent include heating cost"
    definition_period = YEAR


