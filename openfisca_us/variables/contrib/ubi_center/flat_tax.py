from openfisca_us.model_api import *


class flat_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Flat tax"
    unit = USD
    documentation = "Flat income tax on federal AGI."
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        agi = tax_unit("positive_agi", period)
        rate = parameters(period).contrib.ubi_center.flat_tax.rate
        return rate * agi
