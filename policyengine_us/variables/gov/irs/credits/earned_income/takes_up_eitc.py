from policyengine_us.model_api import *


class takes_up_eitc(Variable):
    value_type = bool
    entity = TaxUnit
    label = "takes up the EITC"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        if not hasattr(tax_unit.simulation, "dataset"):
            return True
        takeup_rates = parameters(period).gov.irs.credits.eitc.takeup
        count_children = tax_unit("eitc_child_count", period)
        takeup_rate = takeup_rates.calc(count_children)
        return random(tax_unit) < takeup_rate
