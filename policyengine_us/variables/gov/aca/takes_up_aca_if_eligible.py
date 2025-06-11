from policyengine_us.model_api import *


class takes_up_aca_if_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Whether a random eligible SPM unit does not claim ACA Premium Tax Credit"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        seed = tax_unit("aca_take_up_seed", period)
        takeup_rate = parameters(period).gov.aca.takeup_rate
        return seed < takeup_rate
