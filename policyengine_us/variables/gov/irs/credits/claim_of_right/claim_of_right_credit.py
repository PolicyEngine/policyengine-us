from policyengine_us.model_api import *


class claim_of_right_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Section 1341 credit for repayment of amounts included in income from earlier years"
    unit = USD
    documentation = (
        "When tax is computed under section 1341(a)(5), the decrease in "
        "prior-year tax from excluding the repaid income. It is reported as "
        "a payment (Schedule 3, line 13b), so any excess over the year's tax "
        "is refunded (section 1341(b)(1))."
    )
    definition_period = YEAR
    reference = (
        "https://www.govinfo.gov/content/pkg/USCODE-2024-title26/html/USCODE-2024-title26-subtitleA-chap1-subchapQ-partV-sec1341.htm",
        "https://www.irs.gov/pub/irs-prior/f1040s3--2025.pdf",
        # 2025 Form 1040 instructions, Schedule 3 line 13b
        "https://www.irs.gov/pub/irs-prior/i1040gi--2025.pdf#page=117",
        # Publication 525 (2025), Repayments, method 2
        "https://www.irs.gov/pub/irs-prior/p525--2025.pdf#page=36",
    )

    def formula(tax_unit, period, parameters):
        eligible = tax_unit("claim_of_right_section_1341_eligible", period)
        credit_applies = tax_unit("claim_of_right_credit_applies", period)
        decrease = tax_unit("claim_of_right_prior_year_tax_decrease", period)
        return where(eligible & credit_applies, decrease, 0)
