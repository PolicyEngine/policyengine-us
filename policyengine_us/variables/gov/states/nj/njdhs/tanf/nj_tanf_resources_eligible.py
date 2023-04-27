from policyengine_us.model_api import *


class nj_tanf_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "New Jersey TANF resources eligible"
    definition_period = YEAR
    defined_for = StateCode.NJ

    def formula(spm_unit, period, parameters):
        # The WFNJ/TANF resource limit is $2,000 for an assistance unit.
        # https://www.nj.gov/humanservices/dfd/programs/workfirstnj/tanf_2021_23_st_plan.pdf#page=21
        p = parameters(period).gov.states.nj.njdhs.tanf.eligibility.resources
        countable_resources = spm_unit("nj_tanf_countable_resources", period)
        return countable_resources <= p.limit
