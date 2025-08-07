from policyengine_us.model_api import *


class ok_federal_eitc_phased_in(Variable):
    value_type = float
    entity = TaxUnit
    label = "Federal EITC phase-in amount for the Oklahoma EITC computation"
    unit = USD
    documentation = "EITC maximum amount, taking into account earnings."
    definition_period = YEAR
    defined_for = StateCode.OK

    def formula(tax_unit, period, parameters):
        maximum = tax_unit("ok_federal_eitc_maximum", period)
        phase_in_rate = tax_unit("ok_federal_eitc_phase_in_rate", period)
        earnings = tax_unit("filer_adjusted_earnings", period)
        phased_in_amount = earnings * phase_in_rate
        return min_(maximum, phased_in_amount)
