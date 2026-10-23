from policyengine_us.model_api import *


class mt_federal_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Federal standard or adjusted itemized deduction for Montana"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://mca.legmt.gov/bills/mca/title_0150/chapter_0300/part_0210/section_0200/0150-0300-0210-0200.html",
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2024_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=15",
    )
    defined_for = StateCode.MT

    def formula_2024(tax_unit, period, parameters):
        itemizes = tax_unit("tax_unit_itemizes", period)
        # Use the full allowed federal amount after federal limitations,
        # including any claim of right deduction, and the federal election.
        # The federal model adds wagering losses separately from its general
        # itemized aggregate; they are also part of the allowed itemized amount.
        itemized = add(
            tax_unit,
            period,
            ["itemized_taxable_income_deductions", "wagering_losses_deduction"],
        )
        standard = tax_unit("standard_deduction", period)
        non_itemizer_charity = tax_unit(
            "charitable_deduction_for_non_itemizers", period
        )
        # This display isolates standard/itemized deductions. The taxable-
        # income formula reads the actual federal base, adds QBI back, and
        # keeps Schedule 1-A deductions in that base without deducting them twice.
        federal_deduction = where(itemizes, itemized, standard + non_itemizer_charity)
        add_back = tax_unit("mt_state_income_tax_itemized_add_back", period)
        return max_(0, federal_deduction - add_back)
