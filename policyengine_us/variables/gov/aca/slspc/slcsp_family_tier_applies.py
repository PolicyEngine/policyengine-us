from policyengine_us.model_api import *


class slcsp_family_tier_applies(Variable):
    value_type = bool
    entity = TaxUnit
    label = "ACA family tier applies, rather than age curves"
    definition_period = MONTH

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.aca
        state_code = tax_unit.household("state_code", period)
        return p.family_tier_states[state_code]
