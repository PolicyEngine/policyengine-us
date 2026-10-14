from policyengine_us.model_api import *


class claim_of_right_relief_claimed(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Federal return claims relief for a claim of right repayment"
    documentation = (
        "Whether the federal return claims relief for repaying claim of right "
        "income: the section 1341 credit (Schedule 3, line 13b), or the "
        "repayment deduction (Schedule A, line 16) on a return that itemizes. "
        "A return whose tax is computed with the deduction but that takes the "
        "standard deduction claims neither. Some states allow their own "
        "deduction or subtraction only when the federal return claims one of "
        "the two."
    )
    definition_period = YEAR
    reference = (
        "https://www.govinfo.gov/content/pkg/USCODE-2024-title26/html/USCODE-2024-title26-subtitleA-chap1-subchapQ-partV-sec1341.htm",
        # Publication 525 (2025), Repayments, methods 1 and 2
        "https://www.irs.gov/pub/irs-prior/p525--2025.pdf#page=36",
    )

    def formula(tax_unit, period, parameters):
        eligible = tax_unit("claim_of_right_section_1341_eligible", period)
        credit_applies = tax_unit("claim_of_right_credit_applies", period)
        deduction = tax_unit("claim_of_right_deduction", period)
        itemizes = tax_unit("tax_unit_itemizes", period)
        return eligible & (credit_applies | (itemizes & (deduction > 0)))
