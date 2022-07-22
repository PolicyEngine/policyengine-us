from openfisca_us.model_api import *


class is_breastfeeding(Variable):
    value_type = bool
    entity = Person
    label = "Is breastfeeding"
    definition_period = YEAR
