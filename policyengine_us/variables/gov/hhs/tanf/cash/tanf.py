from policyengine_us.model_api import *


class tanf(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "TANF"
    documentation = (
        "Value of Temporary Assistance for Needy Families benefit received."
    )
    unit = USD

    adds = ["ca_tanf", "co_tanf", "dc_tanf", "ny_tanf"]
