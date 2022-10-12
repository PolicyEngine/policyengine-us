from policyengine_us.model_api import *


class or_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "OR deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.oregonlegislature.gov/bills_laws/ors/ors316.html",  # 316.695 (1)(c)
        "https://www.oregon.gov/dor/forms/FormsPubs/form-or-40_101-040_2021.pdf#page=3",
    )
    defined_for = StateCode.OR

    def formula(tax_unit, period, parameters):
        return max_(
            tax_unit("or_itemized_deductions", period),
            tax_unit("or_standard_deduction", period),
        )
