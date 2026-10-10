from policyengine_us.model_api import *


class mn_claim_of_right_credit_applies(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Minnesota tax is computed with the claim of right credit"
    documentation = (
        "Whether Minnesota income tax for the year of repayment is the tax "
        "without a deduction for the repayment, minus the decrease in the "
        "earlier year's Minnesota tax from excluding the repaid income (the "
        "credit method). Minn. Stat. 290.07, subdivision 4 makes the tax the "
        "lesser of this and the tax computed with the deduction, so the "
        "method is computed, not elected, and it does not depend on the "
        "method 26 U.S.C. 1341 applies to the federal return. When the two "
        "are equal, the tax is computed with the deduction (Minn. R. "
        "8007.0300, subpart 2)."
    )
    definition_period = YEAR
    reference = (
        # Minn. Stat. 290.07, subdivision 4
        "https://www.revisor.mn.gov/statutes/cite/290.07",
        # Minn. R. 8007.0300
        "https://www.revisor.mn.gov/rules/8007.0300/",
        # 2025 Schedule M1REF, line 11
        "https://www.revenue.state.mn.us/sites/default/files/2025-12/m1ref-25.pdf#page=3",
    )
    defined_for = StateCode.MN

    def formula(tax_unit, period, parameters):
        eligible = tax_unit("mn_claim_of_right_eligible", period)
        if not eligible.any():
            # Comparing the two methods takes two more tax computations;
            # skip them when no Minnesota tax unit repays more than the
            # threshold.
            return np.zeros(tax_unit.count, dtype=bool)
        tax_if_credit = tax_unit(
            "mn_income_tax_if_claiming_claim_of_right_credit", period
        )
        tax_if_deduction = tax_unit(
            "mn_income_tax_if_claiming_claim_of_right_deduction", period
        )
        # Ties go to the deduction; the tolerance keeps floating-point noise
        # from deciding a tie.
        TOLERANCE = 0.01
        return eligible & (tax_if_credit < tax_if_deduction - TOLERANCE)
