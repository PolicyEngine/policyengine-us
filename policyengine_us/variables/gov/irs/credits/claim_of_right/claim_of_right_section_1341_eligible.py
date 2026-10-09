from policyengine_us.model_api import *


class claim_of_right_section_1341_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Claim of right repayment qualifies for section 1341"
    documentation = (
        "Whether the repayment of claim of right income on the return "
        "exceeds the section 1341(a)(3) threshold, so that tax is the "
        "lesser of the tax with a deduction for the repayment and the tax "
        "without it less the prior-year tax decrease. The threshold applies "
        "to the total repaid on the return, not to each repayment."
    )
    definition_period = YEAR
    reference = (
        "https://www.govinfo.gov/content/pkg/USCODE-2024-title26/html/USCODE-2024-title26-subtitleA-chap1-subchapQ-partV-sec1341.htm",
        "https://www.ecfr.gov/current/title-26/chapter-I/subchapter-A/part-1/subject-group-ECFR4c74bc8cf7c11fb/section-1.1341-1",
        "https://www.irs.gov/pub/irs-prior/p525--2025.pdf#page=36",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.deductions.itemized.claim_of_right
        repayment = tax_unit("tax_unit_claim_of_right_repayment", period)
        return repayment > p.threshold
