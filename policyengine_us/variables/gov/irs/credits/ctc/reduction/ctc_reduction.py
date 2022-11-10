from policyengine_us.model_api import *


class ctc_reduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "CTC reduction from income"
    unit = USD
    documentation = "Reduction of the total CTC due to income."
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        # TCJA's phase-out changes are purely parametric so don't require
        # structural reform.

        # The ARPA CTC has two phase-outs: the original, and a new phase-out
        # applying before and only to the increase in the maximum CTC under ARPA.

        # Start with the normal phase-out.
        income = tax_unit("adjusted_gross_income", period)
        ctc = parameters(period).gov.irs.credits.ctc
        phase_out_threshold = tax_unit("ctc_phase_out_threshold", period)
        income_over_threshold = max_(0, income - phase_out_threshold)
        reduction = ctc.phase_out.rate * income_over_threshold
        return reduction + tax_unit("ctc_arpa_reduction", period)
