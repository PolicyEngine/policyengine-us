from policyengine_us.model_api import *


class az_tanf_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Arizona TANF resources eligible"
    definition_period = MONTH
    reference = "https://des.az.gov/sites/default/files/dl/tanf_state_plan_oct_2023.pdf#page=20"
    defined_for = StateCode.AZ

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.az.hhs.tanf.resources
        resources = spm_unit("spm_unit_assets", period.this_year)
        return resources <= p.limit
