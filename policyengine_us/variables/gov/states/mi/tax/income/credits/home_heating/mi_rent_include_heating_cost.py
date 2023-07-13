from policyengine_us.model_api import *


class mi_rent_include_heating_cost(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Michigan whether rent included in heating cost"
    definition_period = YEAR
