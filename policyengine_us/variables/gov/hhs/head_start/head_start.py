from policyengine_us.model_api import *


class head_start(Variable):
    value_type = float
    entity = Person
    label = "Amount of Head Start benefit"
    definition_period = YEAR
    defined_for = "is_head_start_eligible"
