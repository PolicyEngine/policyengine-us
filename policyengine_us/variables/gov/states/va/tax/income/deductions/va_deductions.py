from policyengine_us.model_api import *


class va_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/"
        "https://www.tax.virginia.gov/sites/default/files/taxforms/individual-income-tax/2022/760-2022.pdf#page=1"
    )
    defined_for = StateCode.VA

    def formula(tax_unit, period, parameters):
        std_ded = tax_unit("va_standard_deduction", period)
        itm_ded = tax_unit("va_itemized_deductions", period)
        itemizes = tax_unit("tax_unit_itemizes", period)
        return where(itemizes, itm_ded, std_ded)
