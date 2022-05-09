from openfisca_us.model_api import *


class itemizing_dependent_taxable_income_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Itemizing dependent taxable income deductions"
    unit = USD
    documentation = "Taxable income deductions that depend on whether the tax unit itemizes deductions."
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        itemizes = tax_unit("tax_unit_itemizes", period)
        deductions_if_itemizing = tax_unit("taxable_income_deductions_if_itemizing", period)
        deductions_if_not_itemizing = tax_unit("taxable_income_deductions_if_not_itemizing", period)
        return where(itemizes, deductions_if_itemizing, deductions_if_not_itemizing)