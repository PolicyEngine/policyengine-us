from policyengine_us.model_api import *


class household_state_income_tax(Variable):
    # The same sum as state_income_tax, kept for callers that read this name.
    value_type = float
    entity = TaxUnit
    label = "household State tax"
    unit = USD
    definition_period = YEAR
    adds = ["state_income_tax_before_refundable_credits"]
    subtracts = ["state_refundable_credits"]
