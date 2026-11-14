from policyengine_us.model_api import *


class federal_scholarship_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Federal Scholarship Tax Credit"
    unit = USD
    definition_period = YEAR
    defined_for = "federal_scholarship_tax_credit_eligible"
    reference = "https://uscode.house.gov/us/usc/t26/s25F/"

    def formula_2027_01_01(tax_unit, period, parameters):
        available = add(
            tax_unit,
            period,
            [
                "federal_scholarship_tax_credit_potential",
                "federal_scholarship_tax_credit_carryforward",
            ],
        )
        limit = tax_unit("federal_scholarship_tax_credit_credit_limit", period)
        return min_(available, limit)
