from policyengine_us.model_api import *


class tanf(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "TANF"
    documentation = (
        "Value of Temporary Assistance for Needy Families benefit received, "
        "summing all state-specific TANF programs."
    )
    unit = USD
    defined_for = "takes_up_tanf_if_eligible"
    adds = ["tanf_if_takes_up"]
