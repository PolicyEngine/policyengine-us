from openfisca_us.model_api import *


class is_disabled_or_elderly_for_snap(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Is disabled or elderly for SNAP"
    documentation = "Indicates that a person is defined as disabled or elderly based on the USDA definition"
