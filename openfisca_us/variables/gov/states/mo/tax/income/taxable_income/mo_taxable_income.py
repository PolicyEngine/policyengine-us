from openfisca_us.model_api import *


class mo_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Missouri AGI minus deductions"
    unit = USD
    definition_period = YEAR
    reference = "https://dor.mo.gov/forms/MO-A_2021.pdf"

    def formula(tax_unit, period, parameters):
        tax_unit_itemizes = tax_unit("tax_unit_itemizes", period)
        mo_agi = tax_unit("mo_agi", period)
        mo_standard_deduction = tax_unit("mo_standard_deduction", period)
        mo_itemized_deductions = tax_unit("mo_itemized_deductions", period)
        
        return (mo_agi - where(tax_unit_itemizes,mo_itemized_deductions, mo_standard_deduction ))
