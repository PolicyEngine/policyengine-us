from policyengine_us.model_api import *


class nj_tanf_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "New Jersey TANF resources eligible"
    definition_period = YEAR
    defined_for = StateCode.NJ

    def formula(spm_unit, period, parameters):
        # The WFNJ/TANF resource limit is $2,000 for an assistance unit.
        # https://www.state.nj.us/humanservices/providers/grants/public/publicnoticefiles/NJ%20TANF%20State%20Plan%20FFY%2021%20-%20FFY%2023%20DRAFT.pdf#page=20
        p = parameters(period).gov.states.nj.njdhs.tanf.eligibility.resources
        countable_resources = spm_unit("nj_tanf_countable_resources", period)
        return countable_resources <= p.resource_limit
