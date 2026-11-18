from policyengine_us.model_api import *


class state_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "state income tax"
    unit = USD
    definition_period = YEAR
    # Household net income is built from these two totals, so a state's own
    # final tax must equal them. State-specific elections belong in that
    # state's components, not here.
    adds = ["state_income_tax_before_refundable_credits"]
    subtracts = ["state_refundable_credits"]
