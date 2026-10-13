from policyengine_us.model_api import *


class oh_claim_of_right_repayment_qualified_for_credit(Variable):
    value_type = float
    entity = Person
    label = "Claim of right repayment of income that qualified for an Ohio credit"
    unit = USD
    documentation = (
        "Part of claim_of_right_repayment that, in the year the income was "
        "received, qualified for the Ohio nonresident credit or the Ohio "
        "resident credit for tax paid to another state (R.C. 5747.05(A) or "
        "(B)). Ohio's claim of right deduction excludes it."
    )
    definition_period = YEAR
    reference = (
        # R.C. 5747.01(A)(12)(a)
        "https://codes.ohio.gov/ohio-revised-code/section-5747.01",
        "https://codes.ohio.gov/ohio-revised-code/section-5747.05",
    )
    defined_for = StateCode.OH
