from policyengine_us.model_api import *


class ut_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Utah Family Employment Program"
    definition_period = MONTH
    reference = (
        "https://adminrules.utah.gov/public/rule/R986-200/Current%20Rules"
    )
    defined_for = StateCode.UT

    def formula(spm_unit, period, parameters):
        # Per R986-200: Must meet demographic, income, and resource tests
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)
        income_eligible = spm_unit("ut_tanf_income_eligible", period)
        resource_eligible = spm_unit("ut_tanf_resource_eligible", period)
        return demographic_eligible & income_eligible & resource_eligible
