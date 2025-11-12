from policyengine_us.model_api import *
import numpy as np
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant
import numpy as np


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
            base_reduction_uncapped = increments * reduction_amount

            # Option to avoid overlap between regular and ARPA phase-outs
            p_contrib = parameters(period).gov.contrib.ctc.per_child_phase_out
            if p_contrib.avoid_overlap:
                # Sequential application: ARPA phase-out reduces ARPA addition only,
                # then regular phase-out applies to base + remaining ARPA
                # NOTE: ctc_arpa_addition already has ARPA phase-out subtracted,
                # so we only need to return the regular phase-out here
                arpa_addition = tax_unit("ctc_arpa_addition", period)
                base_ctc = tax_unit("ctc_maximum", period)

                # Regular phase-out applies to base CTC + remaining ARPA addition
                ctc_before_regular = base_ctc + arpa_addition
                base_reduction = min_(
                    base_reduction_uncapped, ctc_before_regular
                )

                # Return only the regular phase-out
                # ARPA phase-out is already applied in ctc_arpa_addition
                return base_reduction
            else:
                return base_reduction_uncapped

    class ctc_arpa_uncapped_phase_out(Variable):
        value_type = float
        entity = TaxUnit
        label = "Uncapped phase-out of ARPA CTC increase"
        unit = USD
        definition_period = YEAR

        def formula(tax_unit, period, parameters):
            # Logic sequence follows the form, which is clearer than the IRC.
            p = parameters(period).gov.irs.credits.ctc.phase_out.arpa
            # defined_for didn't work.
            if not p.in_effect:
                return 0
            # The ARPA CTC has two phase-outs: the original, and a new phase-out
            # applying before and only to the increase in the maximum CTC under ARPA.
            # Calculate the income used to assess the new phase-out.
            arpa_threshold = tax_unit("ctc_arpa_phase_out_threshold", period)
            agi = tax_unit("adjusted_gross_income", period)

            # Check if we should cap ARPA phase-out to avoid overlap with regular phase-out
            p_contrib = parameters(period).gov.contrib.ctc.per_child_phase_out
            if p_contrib.avoid_overlap:
                # Cap the ARPA phase-out at the regular phase-out threshold
                # so ARPA only applies to income between its threshold and the regular threshold
                regular_threshold = tax_unit("ctc_phase_out_threshold", period)
                capped_income = min_(agi, regular_threshold)
                excess = max_(0, capped_income - arpa_threshold)
            else:
                excess = max_(0, agi - arpa_threshold)

            increments = np.ceil(excess / p.increment)
            qualifying_children = tax_unit("ctc_qualifying_children", period)
            reduction_amount = p.amount * qualifying_children
            return increments * reduction_amount

    class reform(Reform):
        def apply(self):
            self.update_variable(ctc_phase_out)
            self.update_variable(ctc_arpa_uncapped_phase_out)

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
