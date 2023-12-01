from policyengine_us.model_api import *


class va_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia taxable income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/"
    )
    defined_for = StateCode.VA

    def formula(tax_unit, period, parameters):
        agi = tax_unit("va_afagi", period)
        deductions = tax_unit("va_standard_deduction", period)
        exemptions = tax_unit("va_total_exemptions", period)
        return max_(agi - deductions - exemptions, 0)
