from openfisca_us.model_api import *


class broadband_cost(Variable):
    value_type = float
    entity = SPMUnit
    label = "Broadband cost"
    documentation = "Broadband cost for this SPM unit"
    unit = "currency-USD"
    definition_period = YEAR
