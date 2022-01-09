from openfisca_us.model_api import *


class is_in_school(Variable):
    value_type = bool
    entity = Person
    label = "Is currently in an education institution"
    definition_period = YEAR
