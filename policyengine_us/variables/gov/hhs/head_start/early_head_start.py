from policyengine_us.model_api import *


class early_head_start(Variable):
    value_type = float
    entity = Person
    label = "Amount of Early Head Start benefit"
    definition_period = YEAR
    defined_for = "is_early_head_start_eligible"
