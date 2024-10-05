from openfisca_us.model_api import *


class in_county_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "IN county tax"
    definition_period = YEAR
    unit = USD
    reference = "http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-2-1"  # (a)(3)
    defined_for = StateCode.IN

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states["in"].tax.income.taxes.county
        in_agi = tax_unit("in_agi", period)
        # county calculations are at the person level for each taxpayer in the law
        county = tax_unit.household("county_str", period)
        return in_agi * p.rates[county]
