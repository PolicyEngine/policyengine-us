from openfisca_us.model_api import *


class is_severely_disabled(Variable):
    value_type = bool
    entity = Person
    label = "Is severely disabled"
    definition_period = YEAR
