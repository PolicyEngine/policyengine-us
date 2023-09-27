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
        # 2021 (2022) Form 1040N instructions on page 7 (page 8) say this:
        #   If you use the standard deduction on the federal return,
        #   you must use the Nebraska standard deduction on the
        #   Nebraska return.  All taxpayers that claimed itemized
        #   deductions on their federal return are allowed the larger
        #   of the Nebraska standard deduction or federal itemized
        #   deductions, minus state and local income taxes claimed on
        #   Federal Schedule A.
        federal_itemizer = tax_unit("tax_unit_itemizes", period)
        std_ded = tax_unit("ne_standard_deduction", period)
        itm_ded = tax_unit("ne_itemized_deductions", period)
        deduction = where(federal_itemizer, max_(itm_ded, std_ded), std_ded)
        return max_(0, agi - deduction)
