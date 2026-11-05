from policyengine_us.model_api import *


class household_refundable_federal_tax_credits(Variable):
    value_type = float
    entity = Household
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
