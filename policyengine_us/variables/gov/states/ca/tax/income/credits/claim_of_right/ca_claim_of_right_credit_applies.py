from policyengine_us.model_api import *


class ca_claim_of_right_credit_applies(Variable):
    value_type = bool
    entity = TaxUnit
    label = "California tax is computed with the claim of right credit"
    documentation = (
        "Whether California income tax for the year of repayment is the tax "
        "without a deduction for the repayment, minus the decrease in the "
        "earlier year's California tax from excluding the repaid income (the "
        "credit method). Cal. Rev. & Tax. Code 17049 makes the tax the lesser "
        "of this and the tax computed with the deduction, so the method is "
        "computed, not elected, and it does not depend on the method 26 "
        "U.S.C. 1341 applies to the federal return. When the two are equal, "
        "the model computes the tax with the deduction, as 26 CFR "
        "1.1341-1(b)(3) does for the federal tax."
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
        eligible = tax_unit("ca_claim_of_right_eligible", period)
        if not eligible.any():
            # Comparing the two methods takes two more tax computations;
            # skip them when no California tax unit repays more than the
            # threshold.
            return np.zeros(tax_unit.count, dtype=bool)
        tax_if_credit = tax_unit(
            "ca_income_tax_if_claiming_claim_of_right_credit", period
        )
        tax_if_deduction = tax_unit(
            "ca_income_tax_if_claiming_claim_of_right_deduction", period
        )
        # Ties go to the deduction; the tolerance keeps floating-point noise
        # from deciding a tie.
        TOLERANCE = 0.01
        return eligible & (tax_if_credit < tax_if_deduction - TOLERANCE)
