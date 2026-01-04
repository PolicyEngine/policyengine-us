from policyengine_us.model_api import *


class ut_fep_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Utah Family Employment Program due to resources"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/utah/Utah-Admin-Code-R986-200-230"
    defined_for = StateCode.UT

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ut.dwf.fep.resources.limit
        # Use federal spm_unit_assets variable directly
        assets = spm_unit("spm_unit_assets", period.this_year)
        return assets <= p.amount
