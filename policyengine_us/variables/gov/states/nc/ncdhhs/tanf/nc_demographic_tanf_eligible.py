from policyengine_us.model_api import *


class nc_demographic_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "North Carolina Demographic eligibility for TANF"
    documentation = "Whether any person in a family applying for the Temporary Assistance for Needy Families program meets demographic requirements."
    defined_for = StateCode.NC

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nc.ncdhhs.tanf.eligibility
        person = spm_unit.members
        is_child = person("age", period) < p.age_limit

        household_size = spm_unit("nc_tanf_household_size", period)

        return spm_unit.any(is_child) & (household_size > 0)
