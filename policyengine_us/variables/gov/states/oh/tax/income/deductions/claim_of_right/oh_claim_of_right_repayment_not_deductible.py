from policyengine_us.model_api import *


class oh_claim_of_right_repayment_not_deductible(Variable):
    value_type = float
    entity = Person
    label = "Claim of right repayment that Ohio's repayment deduction excludes"
    unit = USD
    documentation = (
        "Part of claim_of_right_repayment that does not meet R.C. "
        "5747.01(A)(12): income that was not included in Ohio adjusted gross "
        "income in the year it was received (for example, income Ohio "
        "deducted then), income that qualified that year for the Ohio "
        "nonresident credit or the resident credit for tax paid to another "
        "state (R.C. 5747.05(A) or (B)), and amounts that reduce Ohio "
        "adjusted gross income on another line in any year."
    )
    definition_period = YEAR
    reference = (
        # R.C. 5747.01(A)(12)(a) and (b)
        "https://codes.ohio.gov/ohio-revised-code/section-5747.01",
        "https://codes.ohio.gov/ohio-revised-code/section-5747.05",
        # 2025 Ohio IT 1040 instructions, Schedule of Adjustments line 29
        "https://dam.assets.ohio.gov/image/upload/tax.ohio.gov/forms/ohio_individual/individual/2025/it1040-booklet.pdf#page=23",
    )
    defined_for = StateCode.OH
