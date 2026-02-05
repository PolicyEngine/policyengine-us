from policyengine_us.model_api import *


class takes_up_aca_if_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Whether a random eligible SPM unit does not claim ACA Premium Tax Credit"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        draw = tax_unit("aca_takeup_draw", period)
        takeup_rate = parameters(period).gov.aca.takeup_rate
        return draw < takeup_rate
