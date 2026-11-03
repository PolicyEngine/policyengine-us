from policyengine_us.model_api import *


class ne_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "NE itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenue.nebraska.gov/files/doc/tax-forms/2021/f_1040n_booklet.pdf",
        "https://revenue.nebraska.gov/files/doc/2022_Ne_Individual_Income_Tax_Booklet_8-307-2022_final_5.pdf",
        "https://nebraskalegislature.gov/laws/statutes.php?statute=77-2716",
    )
    defined_for = StateCode.NE

    def formula(tax_unit, period, parameters):
        # Nebraska allows federal itemized deductions minus the state and
        # local income taxes claimed on federal Schedule A (see the Form
        # 1040N booklet quoted in ne_taxable_income).
        itm_deds_less_salt = tax_unit("itemized_deductions_less_salt", period)
        # The SALT deduction as claimed federally, after the federal cap.
        federal_salt = tax_unit("salt_deduction", period)
        # Schedule A claims either income taxes or sales taxes, whichever is
        # larger (state_and_local_sales_or_income_tax). Sales taxes stay in
        # the Nebraska deduction.
        income_taxes = add(
            tax_unit, period, ["state_withheld_income_tax", "local_income_tax"]
        )
        sales_taxes = add(tax_unit, period, ["state_sales_tax", "local_sales_tax"])
        claims_income_taxes = income_taxes > sales_taxes
        # When income taxes are claimed, real estate taxes count first toward
        # the capped federal SALT deduction, so the income taxes removed are
        # the rest of it.
        real_estate_taxes = add(tax_unit, period, ["real_estate_taxes"])
        salt_kept = where(
            claims_income_taxes,
            min_(federal_salt, real_estate_taxes),
            federal_salt,
        )
        return itm_deds_less_salt + salt_kept
