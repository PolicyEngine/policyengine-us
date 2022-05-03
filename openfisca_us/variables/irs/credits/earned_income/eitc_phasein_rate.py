from openfisca_us.model_api import *


class eitc_phasein_rate(Variable):
    value_type = float
    entity = TaxUnit
    label = "EITC phase-in rate"
    unit = "/1"
    documentation = "Rate at which the EITC phases in with income."
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        child_count = tax_unit("eitc_child_count", period)
        eitc = parameters(period).irs.credits.eitc
        return eitc.phase_in_rate.calc(child_count)
