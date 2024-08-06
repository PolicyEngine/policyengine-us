from policyengine_us.model_api import *


class state_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "state refundable credits"
    unit = USD
    definition_period = YEAR
    adds = "gov.states.household.state_refundable_credits"
