from policyengine_us.model_api import *


class person_family_id(Variable):
    value_type = int
    entity = Person
    label = "Unique reference for the family of this person"
    definition_period = ETERNITY
