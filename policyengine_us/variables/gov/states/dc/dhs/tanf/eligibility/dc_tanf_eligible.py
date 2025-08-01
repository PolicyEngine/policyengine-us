from policyengine_us.model_api import *


class dc_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for DC Temporary Assistance for Needy Families (TANF)"
    definition_period = MONTH
    reference = "https://dhs.dc.gov/service/tanf-district-families"
    defined_for = StateCode.DC

    def formula(spm_unit, period, parameters):
        meets_basic_eligibility_requirements = spm_unit(
            "dc_tanf_basic_eligibility_requirements", period
        )
        meets_work_requirements = spm_unit(
            "dc_tanf_meets_work_requirements", period
        )
        return meets_basic_eligibility_requirements & meets_work_requirements
