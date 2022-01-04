from openfisca_us.model_api import *


class has_elderly_disabled(Variable):
    value_type = bool
    entity = SPMUnit
    documentation = (
        "Whether elderly or disabled people, per USDA definitions, are present"
    )
    label = "Elderly or disabled person present"
    definition_period = YEAR
