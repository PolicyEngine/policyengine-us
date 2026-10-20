from policyengine_us.model_api import *


class mt_state_income_tax_itemized_add_back(Variable):
    value_type = float
    entity = TaxUnit
    label = (
        "Montana addback of state income tax deducted in federal itemized deductions"
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://mca.legmt.gov/bills/mca/title_0150/chapter_0300/part_0210/section_0200/0150-0300-0210-0200.html",
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2024_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=15",
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2025_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=22",
    )
    defined_for = StateCode.MT

    def formula_2024(tax_unit, period, parameters):
        itemizes = tax_unit("tax_unit_itemizes", period)
        # The federal model adds wagering losses separately from its general
        # itemized aggregate; they are also part of the allowed itemized amount.
        itemized = add(
            tax_unit,
            period,
            ["itemized_taxable_income_deductions", "wagering_losses_deduction"],
        )
        standard = tax_unit("standard_deduction", period)
        salt = tax_unit("salt_deduction", period)
        state_income_tax = add(tax_unit, period, ["state_withheld_income_tax"])
        local_income_tax = add(tax_unit, period, ["local_income_tax"])
        sales_tax = add(tax_unit, period, ["state_sales_tax", "local_sales_tax"])
        income_tax_deducted = state_income_tax + local_income_tax >= sales_tax
        other_taxes = local_income_tax + add(
            tax_unit,
            period,
            ["real_estate_taxes", "mt_federal_itemized_personal_property_taxes"],
        )
        # Worksheet B isolates state income tax after the federal SALT cap.
        # Business-level state tax additions are separate from this ceiling.
        deducted_state_income_tax = min_(state_income_tax, max_(0, salt - other_taxes))
        ceiling = max_(0, itemized - standard)
        return itemizes * income_tax_deducted * min_(deducted_state_income_tax, ceiling)
