from policyengine_us.model_api import *


class hi_claim_of_right_credit_applies(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Hawaii tax is computed with the claim of right tax credit"
    documentation = (
        "Whether Hawaii income tax for the year of repayment is computed "
        "under section 1341(a)(5) as operative in Hawaii: the tax without a "
        "deduction for the repayment, less the decrease in prior-year Hawaii "
        "tax (the Form N-364 credit). Hawaii tax is the lesser of this and "
        "the tax with the deduction, whichever federal method applies; "
        "equal amounts use the deduction."
    )
    definition_period = YEAR
    reference = (
        "https://data.capitol.hawaii.gov/sessions/sessionlaws/Years/SLH2023/SLH2023_Act56.pdf#page=3",
        "https://www.govinfo.gov/content/pkg/USCODE-2024-title26/html/USCODE-2024-title26-subtitleA-chap1-subchapQ-partV-sec1341.htm",
        # 2025 Form N-364 instructions: "whichever results in the least tax",
        # using the Hawaii tax rate.
        "https://files.hawaii.gov/tax/forms/2025/n364_i.pdf",
    )
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        eligible = tax_unit("hi_claim_of_right_section_1341_eligible", period)
        if not eligible.any():
            # Comparing the two methods takes two more Hawaii tax
            # computations; skip them when no tax unit qualifies.
            return np.zeros(tax_unit.count, dtype=bool)
        tax_if_credit = tax_unit(
            "hi_income_tax_if_claiming_claim_of_right_credit", period
        )
        tax_if_deduction = tax_unit(
            "hi_income_tax_if_claiming_claim_of_right_deduction", period
        )
        # Ties go to the deduction (26 CFR 1.1341-1(b)(3)); comparing to the
        # cent keeps floating-point noise from deciding a tie.
        return eligible & (np.round(tax_if_credit, 2) < np.round(tax_if_deduction, 2))
