from policyengine_us.model_api import *


class ca_claim_of_right_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Claim of right repayment qualifies for the California computation"
    documentation = (
        "Whether the repayment of claim of right income on the return exceeds "
        "the California threshold, so that California tax is the lesser of "
        "the tax with a deduction for the repayment and the tax without it "
        "less the decrease in the earlier year's California tax (Cal. Rev. & "
        "Tax. Code 17049)."
    )
    definition_period = YEAR
    reference = (
        # Cal. Rev. & Tax. Code 17049, as amended by Stats. 2005, ch. 349 (AB 1767)
        "https://www.leginfo.ca.gov/pub/05-06/bill/asm/ab_1751-1800/ab_1767_bill_20050922_chaptered.html",
        # 2025 FTB Publication 1001, Claim of right
        "https://www.ftb.ca.gov/forms/2025/2025-1001-publication.pdf#page=25",
        # 2025 Form 540 booklet, Schedule CA (540) Part II line 16
        "https://www.ftb.ca.gov/forms/2025/2025-540-booklet.pdf#page=67",
    )
    defined_for = StateCode.CA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ca.tax.income.credits.claim_of_right
        repayment = tax_unit("tax_unit_claim_of_right_repayment", period)
        return repayment > p.threshold
