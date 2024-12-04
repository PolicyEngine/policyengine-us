from policyengine_us.model_api import *


class household_state_benefits(Variable):
    value_type = float
    entity = Household
    label = "Household state benefits"
    unit = USD
    documentation = "Benefits paid by State agencies."
    definition_period = YEAR
    adds = "gov.household.household_state_benefits"
