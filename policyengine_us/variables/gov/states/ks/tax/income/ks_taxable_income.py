from policyengine_us.model_api import *


class ks_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kansas taxable income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ksrevenue.gov/pdf/ip21.pdf"
        "https://www.ksrevenue.gov/pdf/ip22.pdf"
    )
    defined_for = StateCode.KS

    def formula(tax_unit, period, parameters):
        std_ded = tax_unit("ks_standard_deduction", period)
        itm_ded = tax_unit("ks_itemized_deductions", period)
        deductions = where(itm_ded > std_ded, itm_ded, std_ded)
        exemptions = tax_unit("ks_exemptions", period)
        return max_(0, tax_unit("ks_agi", period) - deductions - exemptions)
