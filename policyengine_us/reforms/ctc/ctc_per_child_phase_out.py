from policyengine_us.model_api import *
import numpy as np
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant


def create_ctc_per_child_phase_out() -> Reform:
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
            income = tax_unit("adjusted_gross_income", period)
            p = parameters(period).gov.irs.credits.ctc.phase_out
            phase_out_threshold = tax_unit("ctc_phase_out_threshold", period)
            qualifying_children = tax_unit("ctc_qualifying_children", period)
            excess = max_(0, income - phase_out_threshold)
            increments = np.ceil(excess / p.increment)
            reduction_amount = p.amount * qualifying_children
            return increments * reduction_amount

    class reform(Reform):
        def apply(self):
            self.update_variable(ctc_phase_out)

    return reform


def create_ctc_per_child_phase_out_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_ctc_per_child_phase_out()

    p = parameters.gov.contrib.ctc.per_child_phase_out

    reform_active = False
    current_period = period_(period)
    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_ctc_per_child_phase_out()
    else:
        return None


ctc_per_child_phase_out = create_ctc_per_child_phase_out_reform(
    None, None, bypass=True
)
