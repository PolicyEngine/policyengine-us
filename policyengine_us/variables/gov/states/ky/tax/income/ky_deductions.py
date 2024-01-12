from policyengine_us.model_api import *


class ky_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kentucky income deductions"
    unit = USD
    definition_period = YEAR
    reference = "https://law.justia.com/codes/kentucky/2022/chapter-141/section-141-019/"  # (2)(i)
    defined_for = StateCode.KY

    def formula(tax_unit, period, parameters):
        return max_(
            tax_unit("ky_itemized_deductions", period),
            tax_unit("ky_standard_deduction", period),
        )
