from policyengine_us.model_api import *


class ne_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "NE taxable income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenue.nebraska.gov/files/doc/tax-forms/2021/f_1040n_booklet.pdf"
        "https://revenue.nebraska.gov/files/doc/2022_Ne_Individual_Income_Tax_Booklet_8-307-2022_final_5.pdf"
    )
    defined_for = StateCode.NE

    def formula(tax_unit, period, parameters):
        agi = tax_unit("ne_agi", period)
        std_ded = tax_unit("ne_standard_deduction", period)
        itm_ded = tax_unit("ne_itemized_deductions", period)
        deductions = where(itm_ded > std_ded, itm_ded, std_ded)
        return max_(0, agi - deductions)
