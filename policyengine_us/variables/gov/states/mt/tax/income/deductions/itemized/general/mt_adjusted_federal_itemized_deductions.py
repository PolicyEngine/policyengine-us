from policyengine_us.model_api import *


class mt_adjusted_federal_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana adjusted federal itemized deductions"
    unit = USD
    definition_period = YEAR
    documentation = (
        "The federal itemized deductions (Form 1040, line 12) less the state "
        "income tax deducted on Schedule A, with the state income tax removed "
        "only down to the federal standard deduction. Montana uses this "
        "amount from 2024, when its taxable income starts from federal "
        "taxable income."
    )
    reference = (
        # MCA 15-30-2120(1) and (2)(j)
        "https://mca.legmt.gov/bills/mca/title_0150/chapter_0300/part_0210/section_0200/0150-0300-0210-0200.html",
        # 2024 Form 2 instructions, line 2 and Worksheet A
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2024_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=15",
        # 2025 Form 2 instructions, line 2, and Schedule I line 4 Worksheet B
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2025_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=13",
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2025_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=22",
    )
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        # Form 1040, line 12: Schedule A, line 17, after any section 68
        # limitation.
        itemized_deductions = tax_unit("itemized_taxable_income_deductions", period)
        # Worksheet B, lines 1-5: the state income tax within the capped SALT
        # deduction, after the local income tax and real estate taxes. Schedule
        # A line 5a holds the larger of income taxes and general sales taxes
        # (state_and_local_sales_or_income_tax); a filer who deducts sales tax
        # deducts no state income tax.
        state_income_tax = tax_unit("state_withheld_income_tax", period)
        local_income_tax = tax_unit("local_income_tax", period)
        sales_tax = add(tax_unit, period, ["state_sales_tax", "local_sales_tax"])
        deducts_income_tax = state_income_tax + local_income_tax >= sales_tax
        real_estate_taxes = add(tax_unit, period, ["real_estate_taxes"])
        salt_deduction = tax_unit("salt_deduction", period)
        state_income_tax_deducted = where(
            deducts_income_tax,
            max_(salt_deduction - local_income_tax - real_estate_taxes, 0),
            0,
        )
        # MCA 15-30-2120(2)(j): the state income tax is added back, but not
        # beyond the amount that brings the itemized deductions down to the
        # federal standard deduction (Worksheet B, lines 6-9).
        standard_deduction = tax_unit("standard_deduction", period)
        itemized_over_standard = max_(itemized_deductions - standard_deduction, 0)
        state_income_tax_addition = min_(
            state_income_tax_deducted, itemized_over_standard
        )
        return itemized_deductions - state_income_tax_addition
