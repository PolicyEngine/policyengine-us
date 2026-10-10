from policyengine_us.model_api import *


class ca_claim_of_right_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "California claim of right repayment deduction"
    unit = USD
    documentation = (
        "California itemized deduction for repaying more than the threshold "
        "of income included in an earlier year under a claim of right, when "
        "California tax is computed with the deduction (17049(a)). Under the "
        "credit method the repayment is not deducted (17049(d)). Schedule CA "
        "(540), Part II, line 16: the filer removes a federal deduction in "
        "column B when taking the California credit, and adds the deduction "
        "in column C when the federal return takes the credit instead. Not "
        "modeled: a repayment of the threshold amount or less, which "
        "California allows as a miscellaneous itemized deduction subject to a "
        "two percent floor. California allows neither when it did not tax the "
        "repaid income; the model treats the whole repayment as taxed by "
        "California."
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
        credit_applies = tax_unit("ca_claim_of_right_credit_applies", period)
        repayment = tax_unit("tax_unit_claim_of_right_repayment", period)
        return where(eligible & ~credit_applies, repayment, 0)
