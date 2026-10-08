from policyengine_us.model_api import *


class mt_state_income_tax_addback(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana state income tax deduction add-back"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT
    reference = (
        "https://mca.legmt.gov/bills/mca/title_0150/chapter_0300/part_0210/section_0200/0150-0300-0210-0200.html",
        "https://revenue.mt.gov/files/Forms/SALT-Cap-Instructions.pdf#page=1",
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2025_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=22",
    )

    def formula(tax_unit, period, parameters):
        itemizes = tax_unit("tax_unit_itemizes", period)
        salt_deduction = tax_unit("salt_deduction", period)
        state_income_tax = max_(0, tax_unit("state_withheld_income_tax", period))
        local_income_tax = tax_unit("local_income_tax", period)
        sales_tax = add(tax_unit, period, ["state_sales_tax", "local_sales_tax"])
        income_tax_elected = state_income_tax + local_income_tax >= sales_tax
        other_salt = tax_unit("salt", period) - tax_unit(
            "state_and_local_sales_or_income_tax", period
        )
        # MCA 15-30-2120(2)(j) reaches only the state income tax deduction
        # claimed. For sales-tax electors the worksheet residual is sales tax.
        state_income_tax_claimed = where(
            income_tax_elected,
            min_(
                state_income_tax,
                max_(0, salt_deduction - local_income_tax - other_salt),
            ),
            0,
        )
        # Schedule A / Form 1040 line 12 includes wagering losses separately
        # from itemized_taxable_income_deductions in deductions_if_itemizing.
        itemized_total = add(
            tax_unit,
            period,
            ["itemized_taxable_income_deductions", "wagering_losses_deduction"],
        )
        standard_deduction = tax_unit("standard_deduction", period)
        excess_itemized = max_(0, itemized_total - standard_deduction)
        return itemizes * min_(state_income_tax_claimed, excess_itemized)
