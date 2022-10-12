from policyengine_us.model_api import *


class tax_unit_size(Variable):
    value_type = int
    entity = TaxUnit
    label = "Tax unit size"
    unit = USD
    documentation = "Number of people in the tax unit"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit.nb_persons()
