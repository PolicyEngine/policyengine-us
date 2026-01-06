from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_ctc_linear_phase_out() -> Reform:
    """
    CTC Linear Phase-Out Reform:
    - Replaces the standard CTC phase-out with a linear phase-out
    - Uses existing IRS threshold for phase-out start
    - Adds new parameter for phase-out end threshold by filing status

    To model full Enhanced CTC policy:
    - Use this reform for linear phase-out
    - Use ctc_minimum_refundable_amount reform for minimum refundability
    - Set existing IRS parameters for credit amounts and phase-in rates

    This reform adds:
    - gov.contrib.ctc.linear_phase_out.in_effect (reform switch)
    - gov.contrib.ctc.linear_phase_out.end (full phase-out by filing status)
    """

    class ctc_phase_out(Variable):
        value_type = float
        entity = TaxUnit
        label = "CTC reduction from income"
        unit = USD
        documentation = (
            "Reduction of the total CTC due to income with linear phase-out."
        )
        definition_period = YEAR

        def formula(tax_unit, period, parameters):
            # Linear phase-out between threshold and end
            p = parameters(period).gov.contrib.ctc.linear_phase_out
            ctc_irs = parameters(period).gov.irs.credits.ctc
            filing_status = tax_unit("filing_status", period)
            income = tax_unit("adjusted_gross_income", period)

            # Use existing IRS threshold for phase-out start
            phase_out_threshold = ctc_irs.phase_out.threshold[filing_status]
            # Use new parameter for phase-out end
            phase_out_end = p.end[filing_status]

            # Calculate the maximum CTC for the tax unit
            ctc_maximum = tax_unit("ctc_maximum_with_arpa_addition", period)

            # Calculate phase-out as linear reduction
            phase_out_range = max_(1, phase_out_end - phase_out_threshold)
            excess_income = max_(0, income - phase_out_threshold)

            # Phase-out rate = ctc_maximum / phase_out_range
            phase_out_rate = ctc_maximum / phase_out_range
            reduction = excess_income * phase_out_rate
            return min_(reduction, ctc_maximum)

    class reform(Reform):
        def apply(self):
            self.update_variable(ctc_phase_out)

    return reform


def create_ctc_linear_phase_out_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_ctc_linear_phase_out()

    p = parameters.gov.contrib.ctc.linear_phase_out

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_ctc_linear_phase_out()
    else:
        return None


ctc_linear_phase_out = create_ctc_linear_phase_out_reform(
    None, None, bypass=True
)
