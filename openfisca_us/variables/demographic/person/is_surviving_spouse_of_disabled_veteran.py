from openfisca_us.model_api import *


class is_surviving_spouse_of_disabled_veteran(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    documentation = "Indicates whether a person is a surviving spouse of a disabled veteran"
    label = "Surviving spouse of disabled veteran"
