from openfisca_us.model_api import *


class state_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "State taxable income"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        agi = tax_unit("adjusted_gross_income", period)
        exemptions = tax_unit("state_income_tax_exemptions", period)
        deductions = tax_unit("state_income_tax_deductions", period)
        return max_(agi - exemptions - deductions, 0)
