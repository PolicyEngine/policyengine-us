from openfisca_us.model_api import *


class ctc_maximum(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maximum CTC"
    unit = USD
    documentation = "Maximum value of the Child Tax Credit, before phaseout."
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return aggr(tax_unit, period, ["ctc_individual_maximum"])
