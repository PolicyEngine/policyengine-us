from policyengine_us.model_api import *


class heating_costs_included_in_rent(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Heating costs are included in the amount rent calculation"
    definition_period = YEAR
   
    