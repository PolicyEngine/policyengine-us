from policyengine_us.model_api import *


class household_tax(Variable):
    value_type = float
    entity = Household
    label = "tax"
    documentation = "Total tax liability after refundable credits."
    unit = USD
    definition_period = YEAR
    adds = ["household_tax_before_refundable_credits"]
    subtracts = ["household_refundable_tax_credits"]
