from policyengine_us.model_api import *
from numpy import ceil


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
        threshold = tax_unit("ctc_arpa_phase_out_threshold", period)
        # Schedule 8812 (2021) line 3: the modified AGI of 24(b)(1), which
        # adds back income excluded under sections 911, 931 and 933.
        magi = tax_unit("agi_plus_section_911_931_933_exclusions", period)
        excess = max_(0, magi - threshold)
        increments = ceil(excess / p.increment)
        return increments * p.amount
