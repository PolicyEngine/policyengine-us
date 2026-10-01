from policyengine_us.model_api import *


class ctc_non_refundable_minimum(Variable):
    value_type = float
    entity = TaxUnit
    label = "CTC that cannot be refunded"
    unit = USD
    documentation = (
        "The part of the Child Tax Credit (including the credit for other "
        "dependents) that exceeds the most that could be refunded, whatever "
        "the tax liability (Schedule 8812 Credit Limit Worksheet B, line 14)."
    )
    definition_period = YEAR
    reference = (
        # 2025 Instructions for Schedule 8812, Credit Limit Worksheet B.
        "https://www.irs.gov/pub/irs-pdf/i1040s8.pdf#page=5",
        "https://www.law.cornell.edu/uscode/text/26/24#d_1",
    )

    def formula(tax_unit, period, parameters):
        ctc = tax_unit("ctc", period)  # Line 1
        refundable_maximum = tax_unit("ctc_refundable_maximum", period)  # Line 2
        phase_in = tax_unit("ctc_phase_in", period)  # Line 12
        most_refundable = min_(refundable_maximum, phase_in)  # Line 13
        return max_(0, ctc - most_refundable)  # Line 14
