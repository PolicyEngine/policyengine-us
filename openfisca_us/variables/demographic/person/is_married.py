from openfisca_us.model_api import *


class is_married(Variable):
    value_type = bool
    entity = Person
    label = "Is married"
    definition_period = YEAR
