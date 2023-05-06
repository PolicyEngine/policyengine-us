from policyengine_us.model_api import *


class mi_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "MI deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.michigan.gov/taxes/iit/retirement-and-pension-benefits/michigan-standard-deduction",
    )
    defined_for = StateCode.MI

    def formula(tax_unit, period, parameters):
        return max_(
            tax_unit("mi_standard_deduction", period),
        )
