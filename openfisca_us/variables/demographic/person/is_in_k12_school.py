from openfisca_us.model_api import *


class is_in_k12_school(Variable):
    value_type = bool
    entity = Person
    label = "Is in a K-12 school"
    definition_period = YEAR
