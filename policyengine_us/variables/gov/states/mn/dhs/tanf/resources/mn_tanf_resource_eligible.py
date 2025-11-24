from policyengine_us.model_api import *


class mn_tanf_resource_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Minnesota MFIP due to resources"
    definition_period = MONTH
    reference = "https://www.revisor.mn.gov/statutes/cite/256P.02"
    defined_for = StateCode.MN

    def formula(spm_unit, period, parameters):
        resources = spm_unit("mn_tanf_countable_resources", period.this_year)
        limit = parameters(period).gov.states.mn.dhs.tanf.resources.limit
        return resources <= limit
