from policyengine_us.model_api import *


class filer_adjusted_earnings(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Filer earned income adjusted for self-employment tax"
    unit = USD

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("adjusted_earnings", tax_unit, period)
