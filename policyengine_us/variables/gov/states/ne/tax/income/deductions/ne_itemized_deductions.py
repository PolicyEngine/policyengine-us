from policyengine_us.model_api import *


class ne_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "NE itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.nebraskalegislature.gov/laws/statutes.php?statute=77-2716.01",
        "https://revenue.nebraska.gov/sites/default/files/doc/tax-forms/2025/f_Individual_Income_Tax_Booklet.pdf#page=14",
        "https://revenue.nebraska.gov/files/doc/tax-forms/2021/f_1040n_booklet.pdf",
        "https://revenue.nebraska.gov/files/doc/2022_Ne_Individual_Income_Tax_Booklet_8-307-2022_final_5.pdf",
    )
    defined_for = StateCode.NE

    def formula(tax_unit, period, parameters):
        itm_deds_less_salt = tax_unit("itemized_deductions_less_salt", period)
        capped_property_taxes = tax_unit("capped_property_taxes", period)
        return itm_deds_less_salt + capped_property_taxes

    def formula_2025(tax_unit, period, parameters):
        federal_itemized = tax_unit("itemized_taxable_income_deductions", period)
        elected_sales_tax = tax_unit("state_and_local_sales_tax_elected", period)
        line_5a = tax_unit("state_and_local_sales_or_income_tax", period)
        # Form 1040N line 8 removes the entire Schedule A line 5a amount
        # when it is income tax, even if the federal SALT cap binds.
        income_tax = where(elected_sales_tax, 0, line_5a)
        # A negative line 9 can never exceed the standard deduction on line 10.
        return max_(0, federal_itemized - income_tax)
