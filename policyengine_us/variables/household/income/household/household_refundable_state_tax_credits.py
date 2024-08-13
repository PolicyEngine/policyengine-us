from policyengine_us.model_api import *


class household_refundable_state_tax_credits(Variable):
    value_type = float
    entity = Household
    label = "refundable State income tax credits"
    unit = USD
    definition_period = YEAR
    adds = "gov.household.household_refundable_state_credits"
