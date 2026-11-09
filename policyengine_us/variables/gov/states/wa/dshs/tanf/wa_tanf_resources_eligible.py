from policyengine_us.model_api import *


class wa_tanf_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Washington TANF resources eligible"
    definition_period = YEAR
    reference = "https://app.leg.wa.gov/wac/default.aspx?cite=388-470-0005"
    defined_for = StateCode.WA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.wa.dshs.tanf
        # Inputs are stored as float32, so compare whole cents with the limit.
        countable_resources = round_to_cents(
            spm_unit("wa_tanf_countable_resources", period)
        )
        return countable_resources <= p.resource_limit
