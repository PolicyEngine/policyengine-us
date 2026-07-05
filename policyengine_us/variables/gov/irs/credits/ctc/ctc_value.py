from policyengine_us.model_api import *


class ctc_value(Variable):
    value_type = float
    entity = TaxUnit
    label = "CTC value"
    unit = USD
    documentation = "Actual value of the Child Tax Credit"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        ctc = tax_unit("ctc", period)
        limiting_tax = tax_unit("ctc_limiting_tax_liability", period)
        refundable_ctc = tax_unit("refundable_ctc", period)
        return min_(ctc, limiting_tax + refundable_ctc)
