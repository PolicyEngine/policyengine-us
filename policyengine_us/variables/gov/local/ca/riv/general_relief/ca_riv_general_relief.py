from policyengine_us.model_api import *


class ca_riv_general_relief(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Riverside County General Relief"
    definition_period = MONTH
    defined_for = "ca_riv_general_relief_eligible"

    adds = [
        "ca_riv_general_relief_needs_standards",
        "ca_riv_general_relief_special_needs_amount",
    ]
    subtracts = ["ca_riv_general_relief_countable_income"]
