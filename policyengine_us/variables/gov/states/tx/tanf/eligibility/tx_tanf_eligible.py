from policyengine_us.model_api import *


class tx_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Texas TANF"
    definition_period = MONTH
    reference = (
        "https://www.hhs.texas.gov/handbooks/texas-works-handbook/a-220-tanf",
        "https://www.hhs.texas.gov/handbooks/texas-works-handbook/a-2420-eligibility-requirements",
    )
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        demographic_eligible = spm_unit("tx_tanf_demographic_eligible", period)
        income_eligible = spm_unit("tx_tanf_income_eligible", period)
        resources_eligible = spm_unit("tx_tanf_resources_eligible", period)

        # Must meet all eligibility requirements
        return demographic_eligible & income_eligible & resources_eligible
