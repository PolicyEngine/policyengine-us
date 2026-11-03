from policyengine_us.model_api import *


class ne_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "NE itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://nebraskalegislature.gov/laws/statutes.php?statute=77-2716.01",
        "https://revenue.nebraska.gov/files/doc/tax-forms/2021/f_1040n_booklet.pdf",
        "https://revenue.nebraska.gov/files/doc/2022_Ne_Individual_Income_Tax_Booklet_8-307-2022_final_5.pdf",
    )
    defined_for = StateCode.NE

    def formula(tax_unit, period, parameters):
        # Neb. Rev. Stat. 77-2716.01(4): federal itemized deductions "except
        # for the amount for state or local income taxes included in federal
        # itemized deductions before any federal disallowance".
        # Form 1040N line 7: federal Schedule A line 17.
        federal_itemized = tax_unit("itemized_taxable_income_deductions", period)
        # Form 1040N line 8: the income taxes on Schedule A line 5a, even when
        # the federal SALT cap limits line 5e, so they are removed in full.
        # Line 5a holds income taxes or general sales taxes, whichever is
        # larger (state_and_local_sales_or_income_tax); a tie counts as sales
        # taxes, and then nothing is removed.
        income_taxes = add(
            tax_unit, period, ["state_withheld_income_tax", "local_income_tax"]
        )
        sales_taxes = add(tax_unit, period, ["state_sales_tax", "local_sales_tax"])
        claims_income_taxes = income_taxes > sales_taxes
        income_taxes_removed = where(claims_income_taxes, income_taxes, 0)
        # Form 1040N line 9 (line 7 minus line 8) can be negative, but line 10
        # takes the larger of it and the standard deduction, so the floor
        # changes no tax.
        return max_(0, federal_itemized - income_taxes_removed)
