from policyengine_us.model_api import *


class ok_tanf_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Oklahoma TANF resources eligible"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/oklahoma/Okla-Admin-Code-SS-340-10-3-5"
    defined_for = StateCode.OK

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ok.dhs.tanf.resources
        # Per OAC 340:10-3-5: Maximum countable reserve is $1,000
        resources = spm_unit("spm_unit_assets", period.this_year)
        return resources <= p.limit
