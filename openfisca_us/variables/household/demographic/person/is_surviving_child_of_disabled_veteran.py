from openfisca_us.model_api import *


class is_surviving_child_of_disabled_veteran(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Surviving child of disabled veteran"
