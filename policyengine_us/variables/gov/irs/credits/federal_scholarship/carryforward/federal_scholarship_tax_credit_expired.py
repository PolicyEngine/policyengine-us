from policyengine_us.model_api import *


class federal_scholarship_tax_credit_expired(Variable):
    value_type = float
    entity = TaxUnit
    label = "Federal Scholarship Tax Credit expiring at year end"
    unit = USD
    definition_period = YEAR
    reference = "https://uscode.house.gov/us/usc/t26/s25F/"

    def formula_2027_01_01(tax_unit, period, parameters):
        p = parameters(period).gov.irs.credits.federal_scholarship
        return tax_unit(
            f"federal_scholarship_tax_credit_carryforward_remaining_{p.carryforward_years}",
            period,
        )
