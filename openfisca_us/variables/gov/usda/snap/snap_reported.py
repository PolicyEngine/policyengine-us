from openfisca_us.model_api import *


class snap_reported(Variable):
    value_type = float
    entity = SPMUnit
    label = "SNAP (reported amount)"
    unit = USD
    documentation = "Reported value of SNAP."
    definition_period = YEAR
