from policyengine_us.model_api import *


class va_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia taxable income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/"
        "https://www.tax.virginia.gov/sites/default/files/taxforms/individual-income-tax/2022/760-2022.pdf#page=1"
    )
    defined_for = StateCode.VA

    def formula(tax_unit, period, parameters):
        afagi = tax_unit("va_afagi", period)
        age_ded = tax_unit("va_age_deduction", period)
        std_ded = tax_unit("va_standard_deduction", period)
        itm_ded = tax_unit("va_itemized_deduction", period)
        vagi = afagi - age_ded
        ded = itm_ded if itm_ded > 0 else std_ded
        exemptions = tax_unit("va_total_exemptions", period)
        return max_(vagi - ded - exemptions, 0)
