from openfisca_us.model_api import *
from openfisca_us.variables.gov.irs.income.taxable_income.deductions.standard_deduction.standard_deduction import (
    standard_deduction)


class md_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD deductions"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        # Check if the tax_unit itemized on their federal returns:
        tax_unit_itemizes = tax_unit("tax_unit_itemizes", period)
        standard_deduction = tax_unit("md_standard_deduction", period)
        deductions_if_itemizing = tax_unit_itemizes * parameters(period).gov.states.md.tax.income.deductions_if_itemizing
        return where(
            tax_unit_itemizes,
            deductions_if_itemizing,
            standard_deduction,
        )
        
        
        