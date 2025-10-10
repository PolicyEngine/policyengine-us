from policyengine_us.model_api import *


class tx_ottanf_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Meets Texas OTTANF resource test"
    definition_period = MONTH
    reference = (
        "https://www.hhs.texas.gov/handbooks/texas-works-handbook/a-2420-eligibility-requirements",
        "https://www.law.cornell.edu/regulations/texas/1-Tex-Admin-Code-SS-372-802",
    )
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        # OTTANF uses same resource limit as regular TANF: $1,000
        countable_resources = spm_unit("tx_tanf_countable_resources", period)
        p = parameters(period).gov.states.tx.tanf.resources

        return countable_resources <= p.resource_limit
