from openfisca_us.model_api import *


class is_permanently_disabled_veteran(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Permanently disabled veteran"
