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
        # Inputs are stored as float32, so compare whole cents with the limit.
        resources = round_to_cents(spm_unit("spm_unit_cash_assets", period.this_year))
        return resources <= p.limit
