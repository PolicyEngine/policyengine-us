from policyengine_us.model_api import *


class tx_tanf_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Meets Texas TANF resource test"
    definition_period = MONTH
    reference = (
        "https://www.hhs.texas.gov/handbooks/texas-works-handbook/a-1220-limits",
        "https://www.hhs.texas.gov/handbooks/texas-works-handbook/a-2420-eligibility-requirements",
    )
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        countable_resources = spm_unit("tx_tanf_countable_resources", period)
        p = parameters(period).gov.states.tx.tanf.resources

        return countable_resources <= p.resource_limit
