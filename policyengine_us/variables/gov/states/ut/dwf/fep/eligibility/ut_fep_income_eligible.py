from policyengine_us.model_api import *


class ut_fep_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Utah Family Employment Program due to income"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/utah/Utah-Admin-Code-R986-200-239"
    defined_for = StateCode.UT

    def formula(spm_unit, period, parameters):
        # Utah uses two-tier income test per R986-200-238
        gross_test = spm_unit("ut_fep_gross_income_eligible", period)
        net_test = spm_unit("ut_fep_net_income_eligible", period)
        return gross_test & net_test
