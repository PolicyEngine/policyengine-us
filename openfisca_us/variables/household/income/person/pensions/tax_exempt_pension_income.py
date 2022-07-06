from openfisca_us.model_api import *


class tax_exempt_pension_income(Variable):
    value_type = float
    entity = Person
    label = "Tax-exempt pension income"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        pension_income = tax_unit("pension_income", period)
        taxable_pension_income = tax_unit("taxable_pension_income", period)
        return pension_income - taxable_pension_income
