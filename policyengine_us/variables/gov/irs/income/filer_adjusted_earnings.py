from policyengine_us.model_api import *


class filer_adjusted_earnings(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Filer earned income adjusted for self-employment tax"
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/32#c_2_A"

    def formula(tax_unit, period, parameters):
        # Per IRS EIC Worksheet B (Form 1040 Instructions), Line 4b:
        # "If line 4b is zero or less, You can't take the credit."
        # The floor applies to the combined tax-unit total, not per-person.
        return max_(
            0, tax_unit_non_dep_sum("adjusted_earnings", tax_unit, period)
        )
