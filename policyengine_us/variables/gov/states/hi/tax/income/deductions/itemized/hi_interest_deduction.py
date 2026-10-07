from policyengine_us.model_api import *


class hi_interest_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii interest deduction"
    unit = USD
    documentation = "Worksheet A-3 line 14: home mortgage and investment interest."
    reference = (
        "https://files.hawaii.gov/tax/forms/2025/n11ins.pdf#page=17",
        "https://files.hawaii.gov/tax/forms/2025/n11ins.pdf#page=34",
    )
    definition_period = YEAR
    defined_for = StateCode.HI

    adds = ["hi_mortgage_interest_deduction", "investment_interest_expense"]
