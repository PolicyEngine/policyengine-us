from openfisca_us.model_api import *


class mo_resident_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "MO resident tax credit"
    unit = USD
    definition_period = YEAR
    reference = ()

    def formula(tax_unit, period, parameters):
        return 0
