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
        # MO agi is defined as federal_agi + mo_additions - mo_subtractions. Since there are no subtractions
        # or additions of note that we model at this time, mo_agi = federal_agi
        mo_agi = tax_unit("adjusted_gross_income", period)
        mo_federal_income_tax_deduction = tax_unit("mo_federal_income_tax_deduction", period)

        # MO standard deduction is set equal to the Federal standard deduction https://revisor.mo.gov/main/OneSection.aspx?section=143.131
        mo_standard_deduction = tax_unit("standard_deduction", period)
        mo_itemized_deductions = tax_unit("mo_itemized_deductions", period)
        
        # NB: The federal income tax deduction applies regardless of itemization.
        return (mo_agi - where(tax_unit_itemizes,mo_itemized_deductions, mo_standard_deduction ) - mo_federal_income_tax_deduction)
