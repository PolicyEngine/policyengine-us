from policyengine_us.model_api import *


class ca_itemized_deductions_pre_limitation(Variable):
    value_type = float
    entity = TaxUnit
    label = "California pre-limitation itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ftb.ca.gov/forms/2021/2021-540-ca-instructions.html",
        "https://www.ftb.ca.gov/forms/2022/2022-540-ca-instructions.html",
        # Schedule CA (540) Part II line 16, claim of right
        "https://www.ftb.ca.gov/forms/2025/2025-540-ca-instructions.html",
        # 2025 Form 540 booklet, Schedule CA (540) instructions, line 16
        "https://www.ftb.ca.gov/forms/2025/2025-540-booklet.pdf#page=67",
    )
    defined_for = StateCode.CA

    # California chooses between its own claim of right deduction and credit
    # whichever method federal tax used (Cal. Rev. & Tax. Code 17049), so the
    # federal repayment deduction comes out (Schedule CA (540), Part II, line
    # 16, column B) and California's goes in (column C).
    adds = [
        "itemized_deductions_less_salt",
        "ca_investment_interest_expense_deduction",
        "real_estate_taxes",
        "ca_claim_of_right_deduction",
    ]
    subtracts = ["investment_interest_expense", "claim_of_right_deduction"]
