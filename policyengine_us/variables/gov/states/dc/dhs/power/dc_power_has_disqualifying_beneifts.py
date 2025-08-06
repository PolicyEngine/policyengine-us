from policyengine_us.model_api import *


class dc_power_has_disqualifying_benefits(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Is receiving disqualifying benefits under DC Program on Work, Employment, and Responsibility (POWER)"
    definition_period = YEAR
    defined_for = StateCode.DC
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/4-205.72#(d)"
    )

    adds = "gov.states.dc.dhs.power.disqualifying_benefits"
