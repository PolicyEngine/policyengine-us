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
        demographic_eligible = (
            add(spm_unit, period, ["mt_tanf_demographic_eligible_person"]) > 0
        )
        income_eligible = spm_unit("mt_tanf_income_eligible", period)
        resources_eligible = spm_unit("mt_tanf_resources_eligible", period)

        meets_work_requirements = spm_unit(
            "mt_tanf_meets_work_requirements", period
        )
        return (
            demographic_eligible
            & meets_work_requirements
            & income_eligible
            & resources_eligible
        )
