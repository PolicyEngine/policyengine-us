from openfisca_us.model_api import *


class mo_federal_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Sum of Federal itemized deductions applicable to MO taxable income calculation"
    unit = USD
    definition_period = YEAR
    reference = "https://dor.mo.gov/forms/MO-A_2021.pdf"

    def formula(tax_unit, period, parameters):
        casualty_loss_deduction = tax_unit("casualty_loss_deduction", period)
        charitable_deduction = tax_unit("charitable_deduction", period)
        interest_deduction = tax_unit("interest_deduction", period)
        itemized_taxable_income_deductions = tax_unit("itemized_taxable_income_deductions", period)
        medical_expense_deduction = tax_unit("medical_expense_deduction", period)
        misc_deduction = tax_unit("misc_deduction", period)

        return (casualty_loss_deduction + charitable_deduction + interest_deduction + itemized_taxable_income_deductions + medical_expense_deduction + misc_deduction) 
