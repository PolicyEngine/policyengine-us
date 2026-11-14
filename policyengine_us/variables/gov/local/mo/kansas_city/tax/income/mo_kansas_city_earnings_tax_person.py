from policyengine_us.model_api import *


class mo_kansas_city_earnings_tax_person(Variable):
    value_type = float
    entity = Person
    label = "Kansas City earnings tax for each person"
    documentation = "Kansas City earnings tax on the person's own taxable earnings."
    definition_period = YEAR
    unit = USD
    reference = "https://www.kcmo.gov/city-hall/departments/finance/earnings-tax"

    def formula(person, period, parameters):
        p = parameters(period).gov.local.mo.kansas_city.tax.income
        taxable_earnings = person(
            "mo_kansas_city_earnings_tax_taxable_earnings", period
        )
        return taxable_earnings * p.rate
