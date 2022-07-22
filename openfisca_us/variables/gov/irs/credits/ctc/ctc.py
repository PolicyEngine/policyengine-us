from openfisca_us.model_api import *


class ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Child Tax Credit"
    unit = USD
    documentation = "Total value of the non-refundable and refundable portions of the Child Tax Credit."
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/24#a"

    def formula(tax_unit, period, parameters):
        maximum_amount = tax_unit("ctc_maximum", period)
        reduction = tax_unit("ctc_reduction", period)
        return maximum_amount - reduction
