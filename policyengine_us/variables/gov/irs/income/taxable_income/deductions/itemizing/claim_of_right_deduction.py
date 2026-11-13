from policyengine_us.model_api import *


class claim_of_right_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Claim of right repayment deduction"
    unit = USD
    documentation = (
        "Itemized deduction for repaying more than the section 1341 threshold "
        "of income included in an earlier year under a claim of right "
        "(Schedule A, line 16), when tax is computed with the deduction "
        "under section 1341(a)(4). It is not a miscellaneous itemized "
        "deduction (section 67(b)(9)), so neither the two percent floor nor "
        "the suspension of those deductions from 2018 applies. Under "
        "section 1341(a)(5) the repayment is not deducted (section "
        "1341(b)(3)). Not modeled: before 2018 a repayment of the threshold "
        "amount or less was a miscellaneous itemized deduction subject to "
        "the two percent floor; from 2018 it is disallowed (section 67(g), "
        "redesignated 67(h) by P.L. 119-21)."
    )
    definition_period = YEAR
    reference = (
        "https://www.govinfo.gov/content/pkg/USCODE-2024-title26/html/USCODE-2024-title26-subtitleA-chap1-subchapQ-partV-sec1341.htm",
        "https://www.law.cornell.edu/uscode/text/26/67#b_9",
        # 2025 Schedule A instructions, line 16, PDF pages 11-12
        "https://www.irs.gov/pub/irs-prior/i1040sca--2025.pdf#page=11",
        # 2017 Schedule A instructions, line 28
        "https://www.irs.gov/pub/irs-prior/i1040sca--2017.pdf#page=13",
    )

    def formula(tax_unit, period, parameters):
        eligible = tax_unit("claim_of_right_section_1341_eligible", period)
        credit_applies = tax_unit("claim_of_right_credit_applies", period)
        repayment = tax_unit("tax_unit_claim_of_right_repayment", period)
        return where(eligible & ~credit_applies, repayment, 0)
