from policyengine_us.model_api import *


class dc_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "DC Temporary Assistance for Needy Families (TANF)"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/4-205.52"
    )
    defined_for = StateCode.DC

    def formula(spm_unit, period, parameters):
        # If a household is receiving POWER, it cannot receive TANF at the same time
        dc_power = spm_unit("dc_power", period)
        dc_tanf_if_claimed = spm_unit("dc_tanf_if_claimed", period)
        return where(dc_power > 0, 0, dc_tanf_if_claimed)
