from policyengine_us.model_api import *


class hi_itemized_deductions_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "May itemize deductions on the Hawaii resident return"
    definition_period = YEAR
    defined_for = StateCode.HI
    reference = "https://files.hawaii.gov/tax/forms/2025/n11ins.pdf#page=15"

    def formula(tax_unit, period, parameters):
        required = tax_unit("hi_required_to_itemize", period)
        itemized = tax_unit("hi_itemized_deductions", period)
        standard = tax_unit("hi_standard_deduction", period)
        return required | (itemized > standard)
