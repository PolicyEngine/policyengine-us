from policyengine_us.model_api import *


class mt_adjusted_federal_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Adjusted federal itemized deductions for Montana reporting"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT
    reference = (
        "https://revenue.mt.gov/files/Forms/SALT-Cap-Instructions.pdf#page=1",
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2025_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=22",
    )

    def formula(tax_unit, period, parameters):
        itemizes = tax_unit("tax_unit_itemizes", period)
        itemized_total = add(
            tax_unit,
            period,
            ["itemized_taxable_income_deductions", "wagering_losses_deduction"],
        )
        addback = tax_unit("mt_state_income_tax_addback", period)
        return itemizes * (itemized_total - addback)
