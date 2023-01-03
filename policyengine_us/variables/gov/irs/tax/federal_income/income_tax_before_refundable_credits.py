from policyengine_us.model_api import *


class income_tax_before_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    unit = USD
    label = "Income tax before refundable credits"
    documentation = "Income tax liability (including other taxes) after non-refundable credits are used, but before refundable credits are applied"
    adds = [
        "income_tax_before_credits",
        "net_investment_income_tax",
        "recapture_of_investment_credit",
        "unreported_payroll_tax",
        "qualified_retirement_penalty",
    ]
    subtracts = ["income_tax_capped_non_refundable_credits"]
