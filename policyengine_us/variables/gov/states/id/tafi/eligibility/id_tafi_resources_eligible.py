from policyengine_us.model_api import *


class id_tafi_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Idaho TAFI resources eligible"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/idaho/IDAPA-16.03.08.200"
    )
    defined_for = StateCode.ID

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.id.tafi.resources
        # Per IDAPA 16.03.08.200: Resources must not exceed $5,000
        resources = spm_unit("spm_unit_assets", period.this_year)
        return resources <= p.limit
