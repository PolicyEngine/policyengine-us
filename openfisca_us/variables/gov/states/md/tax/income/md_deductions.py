from openfisca_us.model_api import *


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
        federal_deductions_if_itemizing = tax_unit_itemizes * tax_unit(
            "taxable_income_deductions_if_itemizing", period
        )
        salt = tax_unit("salt_deduction", period)
        md_deductions = federal_deductions_if_itemizing - salt
        return where(
            tax_unit_itemizes,
            deductions_if_itemizing,
            standard_deduction,
        )
