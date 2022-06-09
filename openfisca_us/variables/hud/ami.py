from openfisca_us.model_api import *


class ami(Variable):
    value_type = float
    entity = SPMUnit
    label = "Area median income"
    documentation = "Area median income"
    definition_period = YEAR
