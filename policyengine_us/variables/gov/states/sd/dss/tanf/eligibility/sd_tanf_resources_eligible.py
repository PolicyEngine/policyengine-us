from policyengine_us.model_api import *


class sd_tanf_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "South Dakota TANF resources eligible"
    definition_period = MONTH
    reference = "https://sdlegislature.gov/Rules/Administrative/67:10:04:03"
    defined_for = StateCode.SD

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.sd.dss.tanf.resources
        resources = spm_unit("spm_unit_assets", period.this_year)
        return resources <= p.limit
