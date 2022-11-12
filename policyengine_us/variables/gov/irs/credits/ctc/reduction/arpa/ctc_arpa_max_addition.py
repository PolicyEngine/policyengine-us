from policyengine_us.model_api import *


class ctc_arpa_max_addition(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maximum additional CTC from ARPA"
    unit = USD
    documentation = (
        "ARPA capped the additional amount based on the phase-out thresholds."
    )
    definition_period = YEAR
    # Defined on Line 5 worksheet of 2021 Instructions for Schedule 8812.
    reference = "https://www.irs.gov/pub/irs-pdf/i1040s8.pdf#page=4"

    def formula(tax_unit, period, parameters):
        # Logic sequence follows the form, which is clearer than the IRC.
        p = parameters(period).gov.irs.credits.ctc.phase_out
        # defined_for didn't work.
        if not p.arpa.in_effect:
            return 0
        filing_status = tax_unit("filing_status", period)
        arpa_threshold = p.arpa.threshold[filing_status]
        original_threshold = tax_unit("ctc_phase_out_threshold", period)
        return (original_threshold - arpa_threshold) * p.arpa.rate
