from policyengine_us.model_api import *


class dc_tanf_basic_eligibility_requirements(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Basic eligibility requirements for DC Temporary Assistance for Needy Families (TANF)"
    definition_period = MONTH
    reference = "https://dhs.dc.gov/service/tanf-district-families"
    defined_for = StateCode.DC

    def formula(spm_unit, period, parameters):
        demographic_eligible = (
            add(spm_unit, period, ["dc_tanf_demographic_eligible_person"]) > 0
        )
        income_eligible = spm_unit("dc_tanf_income_eligible", period)
        resources_eligible = spm_unit("dc_tanf_resources_eligible", period)
        return demographic_eligible & income_eligible & resources_eligible
