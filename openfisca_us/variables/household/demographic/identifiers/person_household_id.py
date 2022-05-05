from openfisca_us.model_api import *


class person_household_id(Variable):
    value_type = int
    entity = Person
    label = "Unique reference for the household of this person"
    definition_period = ETERNITY
