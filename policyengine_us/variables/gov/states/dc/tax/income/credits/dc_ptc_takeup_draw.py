from policyengine_us.model_api import *


class dc_ptc_takeup_draw(Variable):
    value_type = float
    entity = TaxUnit
    label = "Random draw for DC property tax credit take-up"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        if tax_unit.simulation.dataset is not None:
            return random(tax_unit)
        return 0
