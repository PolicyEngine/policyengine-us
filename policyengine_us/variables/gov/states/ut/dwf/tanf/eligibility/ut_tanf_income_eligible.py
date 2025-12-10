from policyengine_us.model_api import *


class ut_tanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Utah Family Employment Program due to income"
    definition_period = MONTH
    reference = (
        "https://adminrules.utah.gov/public/rule/R986-200/Current%20Rules"
    )
    defined_for = StateCode.UT

    def formula(spm_unit, period, parameters):
        # Utah uses two-tier income test per R986-200-238
        gross_test = spm_unit("ut_tanf_gross_income_eligible", period)
        net_test = spm_unit("ut_tanf_net_income_eligible", period)
        return gross_test & net_test
