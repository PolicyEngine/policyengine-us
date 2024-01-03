from policyengine_us.model_api import *


class hi_interest_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii interest deduction"
    unit = USD
    documentation = (
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=17"
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=32"  # total itemized deduction worksheet
    )
    definition_period = YEAR
    defined_for = StateCode.HI

    adds = ["investment_interest_expense", "mortgage_interest"]
