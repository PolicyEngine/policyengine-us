from policyengine_us.model_api import *


class hi_claim_of_right_repayment_excluded_from_income(Variable):
    value_type = float
    entity = Person
    label = "Claim of right repayment not taxed by Hawaii when received"
    unit = USD
    documentation = (
        "Part of claim_of_right_repayment that Hawaii did not tax in the "
        "earlier year it was received. Hawaii allows no deduction or credit "
        "for it."
    )
    definition_period = YEAR
    reference = (
        # 2025 Form N-364 instructions, General Information
        "https://files.hawaii.gov/tax/forms/2025/n364_i.pdf",
    )
    defined_for = StateCode.HI
