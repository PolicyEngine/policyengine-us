from openfisca_us.model_api import *


class no_salt_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Federal taxable income if SALT were abolished"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        itemizes = tax_unit("tax_unit_itemizes", period)
        gov = parameters(period).gov
        federal_itemized_deductions = [
            deduction
            for deduction in gov.irs.deductions.itemized_deductions
            if deduction
            # SALT and QBID both cause circular references.
            not in ["salt_deduction", "qualified_business_income_deduction"]
        ]
        itemized_value = add(tax_unit, period, federal_itemized_deductions)
        agi = tax_unit("adjusted_gross_income", period)
        return where(
            itemizes,
            agi - itemized_value,
            agi - tax_unit("standard_deduction", period),
        )
