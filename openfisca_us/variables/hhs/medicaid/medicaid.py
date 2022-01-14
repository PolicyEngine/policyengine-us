from openfisca_us.model_api import *


class medicaid(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    documentation = "Estimated benefit amount from Medicaid"
    label = "Medicaid benefit"
    unit = USD
