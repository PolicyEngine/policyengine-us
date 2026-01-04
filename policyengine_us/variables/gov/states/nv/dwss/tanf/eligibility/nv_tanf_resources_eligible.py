from policyengine_us.model_api import *


class nv_tanf_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Nevada TANF resources eligible"
    definition_period = MONTH
    reference = "https://dss.nv.gov/TANF/TANF_FAQ-Eligibility_Criteria-R/S/"
    defined_for = StateCode.NV

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nv.dwss.tanf.resource_limit
        # Nevada excludes two vehicles and home, but we use total assets
        # as a simplified approach
        assets = spm_unit("spm_unit_assets", period.this_year)
        return assets <= p.amount
