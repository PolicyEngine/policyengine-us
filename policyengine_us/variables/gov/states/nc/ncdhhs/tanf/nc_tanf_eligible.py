from policyengine_us.model_api import *


class nc_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "North Carolina TANF eligible"
    definition_period = YEAR
    defined_for = StateCode.NC

    def formula(spm_unit, period, parameters):
        has_dependent_child = spm_unit("nc_demographic_tanf_eligible", period)
        income_eligible = spm_unit("nc_tanf_income_eligible", period)

        return income_eligible & has_dependent_child
