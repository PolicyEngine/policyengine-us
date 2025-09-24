from policyengine_us.model_api import *


class mt_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = (
        "Eligible for Montana Temporary Assistance for Needy Families (TANF)"
    )
    definition_period = MONTH
    reference = "https://dphhs.mt.gov/HCSD/tanf"
    defined_for = StateCode.MT

    def formula(spm_unit, period, parameters):
        meets_basic_eligibility_requirements = spm_unit(
            "mt_tanf_basic_eligibility_requirements", period
        )
        meets_work_requirements = spm_unit(
            "mt_tanf_meets_work_requirements", period
        )
        return meets_basic_eligibility_requirements & meets_work_requirements
