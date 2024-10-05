from policyengine_us.model_api import *


class household_id(Variable):
    value_type = int
    entity = Household
    label = "Unique reference for this household"
    definition_period = YEAR
