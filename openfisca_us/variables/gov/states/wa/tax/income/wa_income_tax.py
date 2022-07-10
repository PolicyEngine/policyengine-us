from openfisca_us.model_api import *


class wa_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Washington income tax"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return -tax_unit("wa_working_families_tax_credit", period)
