from openfisca_us.model_api import *


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
        phaseout_start = tax_unit("eitc_phaseout_start", period)
        phaseout_rate = tax_unit("eitc_phaseout_rate", period)
        phaseout_region = max_(0, highest_income_variable - phaseout_start)
        uncapped_reduction = phaseout_rate * phaseout_region
        return min_(uncapped_reduction, tax_unit("eitc_phased_in", period))
