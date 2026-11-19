from policyengine_us.model_api import *
from policyengine_us.tools.state_itemization import state_itemization_uses_itemized


class ca_itemizes(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Itemizes deductions on the California return"
    defined_for = StateCode.CA
    definition_period = YEAR
    reference = "https://www.ftb.ca.gov/forms/2025/2025-540-instructions.html"

    def formula(tax_unit, period, parameters):
        itemized = tax_unit("ca_itemized_deductions", period)
        standard = tax_unit("ca_standard_deduction", period)
        return state_itemization_uses_itemized(
            tax_unit("state_deduction_method", period), itemized > standard
        )
