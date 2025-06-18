from policyengine_us.model_api import *


class ny_ctc_post_2024_phase_out(Variable):
    value_type = float
    entity = TaxUnit
    label = "New York CTC post-2024 phase-out amount"
    documentation = "Amount by which New York CTC is reduced due to income phase-out under post-2024 rules"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/606"  # (c-1)
    defined_for = "ny_ctc_post_2024_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ny.tax.income.credits.ctc
        agi = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)
        base_credit = tax_unit("ny_ctc_post_2024_base", period)

        # Only apply phase-out if there's a base credit and phase-out rate > 0
        phase_out_threshold = p.post_2024.phase_out.threshold[filing_status]
        excess_income = max_(agi - phase_out_threshold, 0)
        # Round up to nearest increment for phase-out calculation
        increment = p.post_2024.phase_out.increment
        excess_increments = (excess_income + increment - 1) // increment
        phase_out_amount = excess_increments * p.post_2024.phase_out.rate

        # Apply phase-out only where there's a base credit and phase-out rate > 0
        has_base_credit = base_credit > 0
        has_phase_out_rate = p.post_2024.phase_out.rate > 0
        apply_phase_out = has_base_credit & has_phase_out_rate

        return apply_phase_out * phase_out_amount
