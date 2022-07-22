from openfisca_us.model_api import *


class snap_assets(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    documentation = "Countable assets for SNAP limits"
    label = "SNAP assets"
    unit = USD
