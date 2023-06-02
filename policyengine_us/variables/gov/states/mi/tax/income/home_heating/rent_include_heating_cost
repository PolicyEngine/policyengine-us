from policyengine_us.model_api import *
class rent_include_heating _cost(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Rent include heating cost"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return add(tax_unit, period, ["rent_include_heating _cost"]) > 0

