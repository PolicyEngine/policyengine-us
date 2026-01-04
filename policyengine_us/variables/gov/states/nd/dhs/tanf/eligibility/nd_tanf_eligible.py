from policyengine_us.model_api import *


class nd_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for North Dakota TANF"
    definition_period = MONTH
    reference = "https://www.nd.gov/dhs/policymanuals/40019/400_19_110_15.htm"
    defined_for = StateCode.ND

    def formula(spm_unit, period, parameters):
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)
        immigration_eligible = (
            add(spm_unit, period, ["is_citizen_or_legal_immigrant"]) > 0
        )
        income_eligible = spm_unit("nd_tanf_income_eligible", period)
        resources_eligible = spm_unit("nd_tanf_resources_eligible", period)
        return (
            demographic_eligible
            & immigration_eligible
            & income_eligible
            & resources_eligible
        )
