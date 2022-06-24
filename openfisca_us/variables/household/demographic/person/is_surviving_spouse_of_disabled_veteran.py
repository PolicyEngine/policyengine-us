from openfisca_us.model_api import *


class is_surviving_spouse_of_disabled_veteran(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Surviving spouse of disabled veteran"
