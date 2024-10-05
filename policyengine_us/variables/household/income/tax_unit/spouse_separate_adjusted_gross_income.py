from policyengine_us.model_api import *


class spouse_separate_adjusted_gross_income(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Spouse's tax unit's adjusted gross income if they file separately"

    # Assume the same characteristics.
    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        return tax_unit("adjusted_gross_income", period) * separate
