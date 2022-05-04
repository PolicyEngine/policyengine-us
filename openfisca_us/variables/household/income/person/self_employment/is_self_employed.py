from openfisca_us.model_api import *


class is_self_employed(Variable):
    value_type = bool
    entity = Person
    label = "Is self-employed"
    documentation = "Whether this person is self-employed."
    definition_period = YEAR
