from policyengine_us.model_api import *


class mo_kansas_city_earnings_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kansas City earnings tax"
    documentation = (
        "Kansas City earnings tax based on explicit taxable earnings inputs."
    )
    definition_period = YEAR
    unit = USD
    reference = "https://www.kcmo.gov/city-hall/departments/finance/earnings-tax"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(period).gov.local.mo.kansas_city.tax.income
        taxable_earnings = person(
            "mo_kansas_city_earnings_tax_taxable_earnings", period
        )
        return tax_unit.sum(taxable_earnings * p.rate)
