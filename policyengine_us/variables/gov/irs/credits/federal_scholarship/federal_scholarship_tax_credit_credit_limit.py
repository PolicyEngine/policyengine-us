from policyengine_us.model_api import *


class federal_scholarship_tax_credit_credit_limit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Federal Scholarship Tax Credit tax-liability limit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://uscode.house.gov/us/usc/t26/s25F/",
        "https://uscode.house.gov/us/usc/t26/s26/",
        "https://uscode.house.gov/us/usc/t26/s24/",
    )

    def formula_2027_01_01(tax_unit, period, parameters):
        p = parameters(period).gov.irs.credits.federal_scholarship
        preceding_credits = add(tax_unit, period, p.preceding_credits)
        liability = max_(
            tax_unit("income_tax_before_credits", period) - preceding_credits, 0
        )
        # Section 24(d)(1)(B) can refund CTC displaced by another subpart A
        # credit. Reading the minimum rather than refundable_ctc avoids a cycle.
        ctc = tax_unit("ctc", period)
        if parameters(period).gov.irs.credits.ctc.refundable.fully_refundable:
            ctc -= tax_unit("refundable_ctc", period)
        ctc = min_(ctc, liability)
        preceding_ctc = where(
            tax_unit("ctc_credit_limit_worksheet_b_applies", period),
            tax_unit("ctc_non_refundable_minimum", period),
            ctc,
        )
        return max_(liability - preceding_ctc, 0)
