from openfisca_us.model_api import *


class property_tax_primary_residence(Variable):
    value_type = float
    entity = TaxUnit
    label = "Property tax for the real estate that includes the principal residence"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit.sum(tax_unit.members("property_tax", period))