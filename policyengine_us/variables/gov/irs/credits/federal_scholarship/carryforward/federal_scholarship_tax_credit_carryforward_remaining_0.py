from policyengine_us.model_api import *


class federal_scholarship_tax_credit_carryforward_remaining_0(Variable):
    value_type = float
    entity = TaxUnit
    label = "Unused current-year Federal Scholarship Tax Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://uscode.house.gov/us/usc/t26/s25F/"

    def formula_2027_01_01(tax_unit, period, parameters):
        potential = tax_unit("federal_scholarship_tax_credit_potential", period)
        carry_in = tax_unit("federal_scholarship_tax_credit_carryforward", period)
        current_used = max_(
            tax_unit("federal_scholarship_tax_credit", period) - carry_in, 0
        )
        return max_(potential - current_used, 0)
