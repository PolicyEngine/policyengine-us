from policyengine_us.model_api import *


class dc_gac_assistance_unit_size(Variable):
    value_type = int
    entity = SPMUnit
    label = "DC General Assistance to Children (GAC) assistance unit size"
    definition_period = MONTH
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/4-205.05a"
    )
    defined_for = StateCode.DC

    adds = ["dc_gac_eligible_child"]
