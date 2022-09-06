from openfisca_us.model_api import *


class rents(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Tax unit pays rent"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):

        return add(tax_unit, period, ["rent"]) > 0
