from policyengine_us.model_api import *


class ny_ctc_post_2024(Variable):
    value_type = float
    entity = TaxUnit
    label = "New York CTC post-2024"
    documentation = "New York's Empire State Child Credit under post-2024 rules (2025-2027)"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/606"  # (c-1)
    defined_for = StateCode.NY

    def formula(tax_unit, period):
        base_credit = tax_unit("ny_ctc_post_2024_base", period)
        phase_out = tax_unit("ny_ctc_post_2024_phase_out", period)

        # Ensure credit cannot go negative
        return max_(base_credit - phase_out, 0)
