from policyengine_us.model_api import *


class il_claim_of_right_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Illinois subtraction for restoring amounts held under a claim of right"
    unit = USD
    documentation = (
        "Illinois base income subtraction for repaying income included in an "
        "earlier year under a claim of right (Schedule M, line 15): the "
        "repayment, when federal tax is computed with the section 1341 credit "
        "or the return deducts the repayment as an itemized deduction. A "
        "return that takes the federal standard deduction under the deduction "
        "method subtracts nothing."
    )
    definition_period = YEAR
    reference = (
        # 35 ILCS 5/203(a)(2)(P)
        "https://ilga.gov/documents/legislation/ilcs/documents/003500050K203.htm",
        # 86 Ill. Adm. Code 100.2465
        "https://my.ilga.gov/commission/jcar/admincode/086/086001000E24650R.html",
        # 2017 Schedule M instructions, line 15
        "https://taxarchive.illinois.gov/content/dam/soi/en/web/taxarchive/forms/income-tax/2017/individual/il-1040-schedule-m-instr.pdf#page=2",
        # 2025 Schedule M instructions, line 15
        "https://tax.illinois.gov/content/dam/soi/en/web/tax/forms/incometax/documents/currentyear/individual/il-1040-schedule-m-instr.pdf#page=3",
    )
    defined_for = StateCode.IL

    def formula(tax_unit, period, parameters):
        # Under the credit method, the subtraction is "the amount of the
        # repayment that would otherwise have been deductible" (86 Ill. Adm.
        # Code 100.2465(b)); under the deduction method, the itemized
        # deduction taken. Either way it is the whole repayment. From 2026 the
        # federal section 68 limit reduces total itemized deductions, not
        # this one, so the deduction taken is still the whole repayment.
        claimed = tax_unit("claim_of_right_relief_claimed", period)
        repayment = tax_unit("tax_unit_claim_of_right_repayment", period)
        return where(claimed, repayment, 0)
