from policyengine_us.model_api import *


class takes_up_dc_ptc(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Takes up the DC property tax credit"
    definition_period = YEAR
    defined_for = StateCode.DC

    def formula(tax_unit, period, parameters):
        draw = tax_unit("dc_ptc_takeup_draw", period)
        rate = parameters(period).gov.states.dc.tax.income.credits.ptc.takeup
        return draw < rate
