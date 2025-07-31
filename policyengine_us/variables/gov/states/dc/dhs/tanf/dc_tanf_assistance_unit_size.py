from policyengine_us.model_api import *


class dc_tanf_assistance_unit_size(Variable):
    value_type = int
    entity = SPMUnit
    label = "DC Temporary Assistance for Needy Families (TANF) assistance unit size"
    definition_period = MONTH
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/4-205.15"
    )
    defined_for = StateCode.DC

    adds = ["spm_unit_size"]
    subtracts = ["dc_gac_assistance_unit_size"]
