from openfisca_us.model_api import *


class is_blind(Variable):
    value_type = bool
    entity = Person
    label = "Is blind"
    definition_period = YEAR
