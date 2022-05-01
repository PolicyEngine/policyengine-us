from openfisca_us.model_api import *


class num(Variable):
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    documentation = "2 when MARS is 2 (married filing jointly); otherwise 1"
    unit = USD

    def formula(tax_unit, period, parameters):
        mars = tax_unit("mars", period)
        return where(mars == mars.possible_values.MARRIED_FILING_JOINTLY, 2, 1)
