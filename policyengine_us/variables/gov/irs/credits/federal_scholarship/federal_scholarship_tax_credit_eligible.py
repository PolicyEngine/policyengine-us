from policyengine_us.model_api import *


class federal_scholarship_tax_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Has current or carried Federal Scholarship Tax Credit"
    definition_period = YEAR
    reference = "https://uscode.house.gov/us/usc/t26/s25F/"

    def formula_2027_01_01(tax_unit, period, parameters):
        return (
            add(
                tax_unit,
                period,
                [
                    "federal_scholarship_tax_credit_potential",
                    "federal_scholarship_tax_credit_carryforward",
                ],
            )
            > 0
        )
