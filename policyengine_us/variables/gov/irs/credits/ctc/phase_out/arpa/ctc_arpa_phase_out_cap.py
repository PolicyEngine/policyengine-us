from policyengine_us.model_api import *


class ctc_arpa_phase_out_cap(Variable):
    value_type = float
    entity = TaxUnit
    label = "Cap on phase-out of ARPA CTC expansion"
    unit = USD
    documentation = (
        "ARPA capped the additional amount based on the phase-out thresholds."
    )
    definition_period = YEAR
    # Defined on Line 5 worksheet of 2021 Instructions for Schedule 8812.
    reference = "https://www.irs.gov/pub/irs-pdf/i1040s8.pdf#page=4"

    def formula(tax_unit, period, parameters):
        # Logic sequence follows the form, which is clearer than the IRC.
        p = parameters(period).gov.irs.credits.ctc
        # defined_for didn't work.
        if not p.phase_out.arpa.in_effect:
            return 0
        arpa_threshold = tax_unit("ctc_arpa_phase_out_threshold", period)
        original_threshold = tax_unit("ctc_phase_out_threshold", period)
        threshold_diff = original_threshold - arpa_threshold
        cap = (
            threshold_diff
            * p.amount.arpa_expansion_cap_percent_of_threshold_diff
        )
        # Form limits the cap to the amount of the increase in the maximum CTC.
        return min_(cap, tax_unit("ctc_arpa_max_addition", period))
