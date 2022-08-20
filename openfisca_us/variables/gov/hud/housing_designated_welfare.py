from openfisca_us.model_api import *


class housing_designated_welfare(Variable):
    value_type = float
    entity = SPMUnit
    label = "Housing designated welfare"
    unit = USD
    definition_period = YEAR
