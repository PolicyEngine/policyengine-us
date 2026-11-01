from policyengine_us.model_api import *


class residential_clean_energy_credit_credit_limit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Residential clean energy credit credit limit"
    definition_period = YEAR
    documentation = (
        "Income tax before credits less every other non-refundable credit, "
        "including the non-refundable Child Tax Credit (Form 5695 Residential "
        "Clean Energy Credit Limit Worksheet)."
    )
    unit = USD
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/25D#c",
        # 2025 Instructions for Form 5695, Residential Clean Energy Credit
        # Limit Worksheet.
        "https://www.irs.gov/pub/irs-pdf/i5695.pdf#page=5",
    )

    def formula(tax_unit, period, parameters):
        income_tax_before_credits = tax_unit("income_tax_before_credits", period)
        p = parameters(period).gov.irs.credits.residential_clean_energy
        preceding_credits = add(tax_unit, period, p.preceding_credits)
        liability_after_preceding_credits = max_(
            income_tax_before_credits - preceding_credits, 0
        )
        # The Child Tax Credit and credit for other dependents also precede
        # this credit (Form 1040, line 19). When Schedule 8812 Credit Limit
        # Worksheet B applies, only the part of the CTC that cannot be refunded
        # counts (Worksheet B, line 14): this credit uses the liability first
        # and the CTC it displaces is refunded instead.
        ctc = tax_unit("ctc", period)
        if parameters(period).gov.irs.credits.ctc.refundable.fully_refundable:
            # The refundable CTC does not depend on tax liability in these
            # years, so it can be read here without a circular dependency.
            ctc_not_refunded = ctc - tax_unit("refundable_ctc", period)
        else:
            ctc_not_refunded = ctc
        non_refundable_ctc = min_(ctc_not_refunded, liability_after_preceding_credits)
        preceding_ctc = where(
            tax_unit("ctc_credit_limit_worksheet_b_applies", period),
            tax_unit("ctc_non_refundable_minimum", period),
            non_refundable_ctc,
        )
        return max_(liability_after_preceding_credits - preceding_ctc, 0)
