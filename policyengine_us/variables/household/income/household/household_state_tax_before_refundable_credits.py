from policyengine_us.model_api import *


class household_state_tax_before_refundable_credits(Variable):
    value_type = float
    entity = Household
    label = "household State tax before refundable credits"
    unit = USD
    definition_period = YEAR
    adds = "gov.household_tax_before_refundable_credits"
    exhaustive_parameter_dependencies = "gov.states"
