from policyengine_us.model_api import *


class ut_fep_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Utah Family Employment Program"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/utah/Utah-Admin-Code-R986-200-202"
    defined_for = StateCode.UT

    def formula(spm_unit, period, parameters):
        # Per R986-200: Must meet demographic, income, and resource tests
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)
        income_eligible = spm_unit("ut_fep_income_eligible", period)
        resource_eligible = spm_unit("ut_fep_resources_eligible", period)
        return demographic_eligible & income_eligible & resource_eligible
