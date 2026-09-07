from policyengine_us.model_api import *


class parent_1_id(Variable):
    value_type = int
    entity = Person
    label = "First co-resident parent's person ID"
    definition_period = YEAR
    default_value = 0
    documentation = "person_id of a co-resident parent; 0 when unknown"
