from policyengine_us.model_api import *


class mt_federal_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Federal taxable income for Montana Form 2 line 3"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT
    reference = (
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2/2024_Montana_Individual_Income_Tax_Return_Form_2.pdf#page=1",
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2/2025_Montana_Individual_Income_Tax_Return_Form_2.pdf#page=1",
    )

    def formula(tax_unit, period, parameters):
        agi = tax_unit("adjusted_gross_income", period)
        exemptions = tax_unit("exemptions", period)
        deductions = tax_unit("mt_federal_deductions", period)
        return max_(0, agi - exemptions - deductions)
