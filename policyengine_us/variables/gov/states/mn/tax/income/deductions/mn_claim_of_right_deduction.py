from policyengine_us.model_api import *


class mn_claim_of_right_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota claim of right repayment deduction"
    unit = USD
    documentation = (
        "Minnesota itemized deduction for repaying more than the threshold of "
        "income included in an earlier year under a claim of right, when "
        "Minnesota tax is computed with the deduction (290.07, subdivision "
        "4). Under the credit method the repayment is not deducted (Minn. R. "
        "8007.0300, subpart 2). Minnesota itemized deductions include the "
        "deduction under section 1341 of the Internal Revenue Code (Minn. "
        "Stat. 290.0122, subdivision 9(4); Schedule M1SA, line 24). Not "
        "modeled: a repayment of the threshold amount or less, which "
        "Minnesota allows as a miscellaneous itemized deduction subject to a "
        "two percent floor."
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
        credit_applies = tax_unit("mn_claim_of_right_credit_applies", period)
        repayment = tax_unit("tax_unit_claim_of_right_repayment", period)
        return where(eligible & ~credit_applies, repayment, 0)
