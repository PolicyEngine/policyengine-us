from policyengine_us.model_api import *


class eitc_reduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "EITC reduction"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/32#a_2"

    def formula(tax_unit, period, parameters):
        earnings = tax_unit("filer_earned", period)
        highest_income_variable = max_(
            earnings, tax_unit("adjusted_gross_income", period)
        )
        phase_out_start = tax_unit("eitc_phase_out_start", period)
        phase_out_rate = tax_unit("eitc_phase_out_rate", period)
        phase_out_region = max_(0, highest_income_variable - phase_out_start)
        return phase_out_rate * phase_out_region
