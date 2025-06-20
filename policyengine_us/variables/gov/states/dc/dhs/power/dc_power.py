from policyengine_us.model_api import *


class dc_power(Variable):
    value_type = float
    entity = SPMUnit
    label = "DC Program on Work, Employment, and Responsibility (POWER)"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/4-205.52"
    )
    defined_for = "dc_power_eligible"

    adds = ["dc_tanf_if_claimed"]
