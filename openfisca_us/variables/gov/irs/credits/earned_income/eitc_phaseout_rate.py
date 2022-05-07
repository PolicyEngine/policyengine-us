from openfisca_us.model_api import *


class eitc_phaseout_rate(Variable):
    value_type = float
    entity = TaxUnit
    label = "EITC phase-out rate"
    unit = USD
    documentation = "Percentage of earnings above the phase-out threshold that reduce the EITC."
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        eitc = parameters(period).irs.credits.eitc
        num_children = tax_unit("eitc_child_count", period)
        return eitc.phaseout.rate.calc(num_children)
