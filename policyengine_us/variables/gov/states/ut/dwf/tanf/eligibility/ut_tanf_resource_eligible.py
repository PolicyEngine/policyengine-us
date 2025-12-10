from policyengine_us.model_api import *


class ut_tanf_resource_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Utah Family Employment Program due to resources"
    definition_period = MONTH
    reference = (
        "https://adminrules.utah.gov/public/rule/R986-200/Current%20Rules"
    )
    defined_for = StateCode.UT

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ut.dwf.tanf.resources.limit
        # Use federal spm_unit_assets variable directly
        assets = spm_unit("spm_unit_assets", period.this_year)
        return assets <= p.amount
