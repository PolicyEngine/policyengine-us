from openfisca_us.model_api import *


class person_weight(Variable):
    value_type = float
    entity = Person
    label = "Person weight"
    definition_period = YEAR
