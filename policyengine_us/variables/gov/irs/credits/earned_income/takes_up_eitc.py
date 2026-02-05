from policyengine_us.model_api import *


class takes_up_eitc(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Takes up the EITC"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        draw = tax_unit("eitc_takeup_draw", period)
        child_count = tax_unit("eitc_child_count", period)
        rate = parameters(period).gov.irs.credits.eitc.takeup.calc(child_count)
        return draw < rate
