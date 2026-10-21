from policyengine_us.model_api import *
from numpy import ceil


class ctc_phase_out(Variable):
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
        # 26 U.S.C. 24(b)(1): modified adjusted gross income adds back
        # income excluded under sections 911, 931 and 933.
        income = tax_unit("agi_plus_section_911_931_933_exclusions", period)
        p = parameters(period).gov.irs.credits.ctc.phase_out
        phase_out_threshold = tax_unit("ctc_phase_out_threshold", period)
        excess = max_(0, income - phase_out_threshold)
        increments = ceil(excess / p.increment)
        return increments * p.amount
