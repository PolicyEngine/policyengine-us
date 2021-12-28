from openfisca_us.model_api import *


class is_disabled_or_elderly_for_snap(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Is disabled or elderly for SNAP"
    documentation = "Indicates that a person is defined as disabled or elderly based on the USDA definition"


class has_elderly_disabled(Variable):
    value_type = bool
    entity = SPMUnit
    documentation = (
        "Whether elderly or disabled people, per USDA definitions, are present"
    )
    label = "Elderly or disabled person present"
    definition_period = YEAR
