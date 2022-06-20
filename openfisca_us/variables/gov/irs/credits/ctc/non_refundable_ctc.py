from openfisca_us.model_api import *


class non_refundable_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Non-refundable CTC"
    unit = USD
    documentation = (
        "The portion of the Child Tax Credit that is not refundable."
    )
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit("ctc", period) - tax_unit("refundable_ctc", period)
