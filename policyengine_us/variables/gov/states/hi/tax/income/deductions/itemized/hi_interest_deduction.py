from policyengine_us.model_api import *


class hi_interest_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii interest deduction"
    unit = USD
    reference = (
        # 2022 N-11 instructions, line 21c and the total itemized deduction
        # worksheet, PDF pages 17, 32
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=17",
        # Tax Announcement 2021-01: supplemental instructions for the
        # mortgage insurance premiums itemized deduction
        "https://files.hawaii.gov/tax/news/announce/ann21-01.pdf",
    )
    definition_period = YEAR
    defined_for = StateCode.HI

    adds = [
        "investment_interest_expense",
        "hi_mortgage_interest_deduction",
        "hi_deductible_mortgage_insurance_premiums",
    ]
