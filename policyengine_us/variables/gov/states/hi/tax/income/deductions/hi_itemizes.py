from policyengine_us.model_api import *
from policyengine_us.tools.state_itemization import state_itemization_uses_itemized


class hi_itemizes(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Itemizes deductions on the Hawaii resident return"
    definition_period = YEAR
    defined_for = StateCode.HI
    reference = (
        "https://files.hawaii.gov/tax/forms/2025/n11ins.pdf#page=15",
        "https://files.hawaii.gov/tax/news/announce/ann26-06.pdf#page=2",
    )

    def formula(tax_unit, period, parameters):
        required = tax_unit("hi_required_to_itemize", period)
        eligible = tax_unit("hi_itemized_deductions_eligible", period)
        itemized = tax_unit("hi_itemized_deductions", period)
        standard = tax_unit("hi_standard_deduction", period)
        nonitemizer_charity = tax_unit("charitable_deduction_for_non_itemizers", period)
        itemizes = state_itemization_uses_itemized(
            tax_unit("state_deduction_method", period),
            itemized > standard + nonitemizer_charity,
        )
        return required | (eligible & itemizes)
