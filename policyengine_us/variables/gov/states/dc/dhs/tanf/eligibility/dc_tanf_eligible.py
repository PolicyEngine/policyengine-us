from policyengine_us.model_api import *


class dc_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for DC Temporary Assistance for Needy Families (TANF)"
    definition_period = MONTH
    defined_for = StateCode.DC

    def formula(spm_unit, period, parameters):
        demographic_eligible = add(
            spm_unit, period, ["dc_tanf_eligible_demographic"]
        )
        income_eligible = spm_unit("dc_tanf_income_eligible", period)
        resources_eligible = spm_unit("dc_tanf_resources_eligible", period)
        immigration_status_eligible = add(
            spm_unit, period, ["dc_tanf_eligible_immigration_status"]
        )
        return (
            demographic_eligible
            & income_eligible
            & resources_eligible
            & immigration_status_eligible
        )
