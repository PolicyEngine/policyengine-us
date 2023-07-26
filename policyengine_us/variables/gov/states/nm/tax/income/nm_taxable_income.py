from policyengine_us.model_api import *


class nm_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico taxable income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NM

    def formula(tax_unit, period, parameters):
        nm_agi = tax_unit("nm_agi", period)
        deductions = tax_unit("nm_deductions", period)
        exemptions = tax_unit("nm_exemptions", period)
        other_subtractions = tax_unit("nm_subtractions", period)
        return max_(0, nm_agi - deductions - exemptions - other_subtractions)
