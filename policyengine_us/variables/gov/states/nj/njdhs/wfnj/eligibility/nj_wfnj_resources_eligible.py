from policyengine_us.model_api import *


class nj_wfnj_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "New Jersey WFNJ resources eligible"
    definition_period = MONTH
    defined_for = StateCode.NJ
    reference = (
        "https://www.law.cornell.edu/regulations/new-jersey/N-J-A-C-10-90-3-20"
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nj.njdhs.wfnj.resources
        resources = spm_unit("spm_unit_assets", period.this_year)
        return resources <= p.limit
