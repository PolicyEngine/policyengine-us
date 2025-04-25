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
        p = parameters(period).gov.irs.credits.ctc.refundable
        if not p.fully_refundable:
            phase_in = tax_unit("ctc_phase_in", period)
            return min_(ctc, phase_in)
        return ctc
