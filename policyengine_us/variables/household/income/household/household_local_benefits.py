from policyengine_us.model_api import *


class household_local_benefits(Variable):
    value_type = float
    entity = Household
    label = "Household local benefits"
    unit = USD
    documentation = "Benefits paid by local agencies."
    definition_period = YEAR
    adds = "gov.household.household_local_benefits"
