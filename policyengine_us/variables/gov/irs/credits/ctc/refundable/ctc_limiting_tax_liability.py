from policyengine_us.model_api import *


class ctc_limiting_tax_liability(Variable):
    value_type = float
    entity = TaxUnit
    label = "CTC-limiting tax liability"
    unit = USD
    documentation = (
        "The tax liability used to determine the maximum amount of the "
        "non-refundable CTC (Schedule 8812 Credit Limit Worksheet A, line 5): "
        "income tax before credits less the credits that precede the CTC, "
        "less the residential clean energy credit when Credit Limit Worksheet "
        "B applies. Excludes SALT from income tax before credits (this is an "
        "inaccuracy required to avoid circular dependencies)."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/26#a",
        "https://www.law.cornell.edu/uscode/text/26/24#d_1_B",
        # 2025 Instructions for Schedule 8812, Credit Limit Worksheets A and B.
        "https://www.irs.gov/pub/irs-pdf/i1040s8.pdf#page=4",
        "https://www.irs.gov/pub/irs-pdf/i1040s8.pdf#page=6",
    )

    def formula(tax_unit, period, parameters):
        liability_after_preceding_credits = tax_unit(
            "ctc_tax_liability_after_preceding_credits", period
        )  # Line 3
        # Section 25D(c) orders the residential clean energy credit after the
        # CTC, but section 24(d)(1)(B) refunds the CTC by the increase in all
        # subpart A credits. Worksheet B therefore lets that credit use the
        # liability first, moving the displaced CTC into the refundable part.
        p = parameters(period).gov.irs.credits.ctc_tax_liability_limit
        # add() returns None for an empty list, which a reform may set.
        subsequent_credits = (
            add(tax_unit, period, p.subsequent_credits) if p.subsequent_credits else 0
        )
        worksheet_b_applies = tax_unit("ctc_credit_limit_worksheet_b_applies", period)
        worksheet_b_amount = where(worksheet_b_applies, subsequent_credits, 0)  # Line 4
        return max_(0, liability_after_preceding_credits - worksheet_b_amount)  # Line 5
