from openfisca_us.model_api import *


class or_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "OR taxable income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.OR

    def formula(tax_unit, period, parameters):
        return tax_unit("or_income_after_subtractions", period) - tax_unit("or_deductions", period) - 
