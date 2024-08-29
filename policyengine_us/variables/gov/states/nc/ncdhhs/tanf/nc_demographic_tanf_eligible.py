from policyengine_us.model_api import *


class nc_demographic_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "North Carolina Demographic eligibility for TANF"
    documentation = "Whether any person in a family applying for the Temporary Assistance for Needy Families program meets demographic requirements."
    defined_for = StateCode.NC

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        is_child = person("is_child", period)

        return spm_unit.any(is_child)
