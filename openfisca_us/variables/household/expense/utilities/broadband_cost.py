from openfisca_us.model_api import *


class broadband_cost(Variable):
    value_type = float
    entity = SPMUnit
    label = "Broadband cost"
    unit = USD
    definition_period = YEAR
