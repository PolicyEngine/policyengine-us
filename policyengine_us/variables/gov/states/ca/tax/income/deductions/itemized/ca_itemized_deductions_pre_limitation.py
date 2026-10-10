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
    )
    defined_for = StateCode.CA

    adds = [
        "itemized_deductions_less_salt",
        "ca_investment_interest_expense_deduction",
        "real_estate_taxes",
    ]
    # California chooses between its own claim of right deduction and credit
    # whichever method federal tax used, and allows neither for income it did
    # not tax, so the federal deduction does not carry over. California's own
    # rule is not modeled.
    subtracts = ["investment_interest_expense", "claim_of_right_deduction"]
