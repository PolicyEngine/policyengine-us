from policyengine_us.model_api import *


class eitc_phased_in(Variable):
    value_type = float
    entity = TaxUnit
    label = "EITC phase-in amount"
    unit = USD
    documentation = "EITC maximum amount, taking into account earnings."
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        maximum = tax_unit("eitc_maximum", period)
        phase_in_rate = tax_unit("eitc_phase_in_rate", period)
        earnings = tax_unit("filer_adjusted_earnings", period)
        phased_in_amount = earnings * phase_in_rate
        return min_(maximum, phased_in_amount)
