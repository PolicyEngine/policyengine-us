from policyengine_us.model_api import *


class spouse_separate_tax_unit_size(Variable):
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    label = "Size of spouse's tax unit if they file separately"

    # Assume the same characteristics.
    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        return tax_unit("tax_unit_size", period) * separate
