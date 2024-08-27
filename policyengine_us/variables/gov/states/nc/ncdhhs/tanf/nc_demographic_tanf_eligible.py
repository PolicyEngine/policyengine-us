from policyengine_us.model_api import *

class nc_demographic_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "NC Demographic eligibility for TANF"
    documentation = "Whether any person in a family applying for the Temporary Assistance for Needy Families program meets demographic requirements."
    adds = ["nc_tanf_child_eligible"]

    def formula(spm_unit, period, parameters):
        # Check if any person in the SPMUnit is eligible as a child for TANF
        return spm_unit.any("nc_tanf_child_eligible", period)
