from policyengine_us.model_api import *


class income_tax_refundable_credits_in_force(Variable):
    value_type = float
    # On the tax unit, so household_refundable_tax_credits maps it up in float64
    # and sums the household total to the same bits as main's direct read of
    # income_tax_refundable_credits. A household variable would come back in
    # float32 and shift the total by a rounding step.
    entity = TaxUnit
    label = "refundable federal income tax credits"
    documentation = (
        "Federal refundable income tax credits counted in household net "
        "income. They are zero in a year the federal income tax is abolished, "
        "because income_tax, which nets them, is zero then."
    )
    definition_period = YEAR
    unit = USD
    defined_for = "federal_income_tax_in_force"
    adds = ["income_tax_refundable_credits"]
