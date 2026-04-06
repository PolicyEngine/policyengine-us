from policyengine_us.model_api import *


class mt_tanf_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Montana Temporary Assistance for Needy Families (TANF) due to resources"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/montana/Mont-Admin-r-37.78.401"
    defined_for = StateCode.MT

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.mt.dhs.tanf.resource_limit
        countable_resources = spm_unit("mt_tanf_countable_resources", period)
        return countable_resources <= p.amount
