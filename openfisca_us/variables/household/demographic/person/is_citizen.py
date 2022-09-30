from openfisca_us.model_api import *


class is_citizen(Variable):
    value_type = bool
    entity = Person
    label = "Is a U.S. citizen"
    definition_period = YEAR
    question = "Are you a U.S. citizen?"
