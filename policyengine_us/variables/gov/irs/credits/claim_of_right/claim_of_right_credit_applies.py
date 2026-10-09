from policyengine_us.model_api import *


class claim_of_right_credit_applies(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Tax is computed under section 1341(a)(5)"
    documentation = (
        "Whether federal income tax for the year of repayment is computed "
        "under 26 U.S.C. 1341(a)(5): the tax without a deduction for the "
        "repayment, minus the decrease in prior-year tax from excluding the "
        "repaid income (the credit method). Section 1341 makes the tax the "
        "lesser of this and the tax computed with the deduction under "
        "1341(a)(4), so the method is computed, not elected. When the two "
        "are equal, the tax is computed under 1341(a)(4)."
    )
    definition_period = YEAR
    reference = (
        "https://www.govinfo.gov/content/pkg/USCODE-2024-title26/html/USCODE-2024-title26-subtitleA-chap1-subchapQ-partV-sec1341.htm",
        # 26 CFR 1.1341-1(b)(1) and (b)(3)
        "https://www.ecfr.gov/current/title-26/chapter-I/subchapter-A/part-1/subject-group-ECFR4c74bc8cf7c11fb/section-1.1341-1",
        # Publication 525 (2025), Repayments, methods 1 and 2
        "https://www.irs.gov/pub/irs-prior/p525--2025.pdf#page=36",
    )

    def formula(tax_unit, period, parameters):
        eligible = tax_unit("claim_of_right_section_1341_eligible", period)
        if not eligible.any():
            # Comparing the two methods takes two more tax computations;
            # skip them when no tax unit repays more than the threshold.
            return np.zeros(tax_unit.count, dtype=bool)
        tax_if_credit = tax_unit("income_tax_if_claiming_claim_of_right_credit", period)
        tax_if_deduction = tax_unit(
            "income_tax_if_claiming_claim_of_right_deduction", period
        )
        # Ties go to the deduction (26 CFR 1.1341-1(b)(3)); the tolerance
        # keeps floating-point noise from deciding a tie.
        TOLERANCE = 0.01
        return eligible & (tax_if_credit < tax_if_deduction - TOLERANCE)
