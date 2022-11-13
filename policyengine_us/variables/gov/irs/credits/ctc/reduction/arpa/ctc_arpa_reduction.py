from policyengine_us.model_api import *


class ctc_arpa_reduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Additional CTC ARPA reduction"
    unit = USD
    documentation = "Additional ARPA reduction of the total CTC due to income."
    definition_period = YEAR
    # Defined on Line 5 worksheet of 2021 Instructions for Schedule 8812.
    reference = "https://www.irs.gov/pub/irs-pdf/i1040s8.pdf#page=4"

    def formula(tax_unit, period, parameters):
        # Logic sequence follows the form, which is clearer than the IRC.
        ctc = parameters(period).gov.irs.credits.ctc
        # defined_for didn't work.
        if not ctc.phase_out.arpa.in_effect:
            return 0
        # The ARPA CTC has two phase-outs: the original, and a new phase-out
        # applying before and only to the increase in the maximum CTC under ARPA.
        # Calculate the income used to assess the new phase-out.
        filing_status = tax_unit("filing_status", period)
        arpa_threshold = ctc.phase_out.arpa.threshold[filing_status]
        agi = tax_unit("adjusted_gross_income", period)
        excess = max_(0, agi - arpa_threshold)
        return excess * ctc.phase_out.arpa.rate
