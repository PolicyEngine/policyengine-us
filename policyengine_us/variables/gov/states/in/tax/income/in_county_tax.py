from policyengine_us.model_api import *


class in_county_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Indiana county tax"
    definition_period = YEAR
    unit = USD
    reference = "http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-2-1"  # (a)(3)
    defined_for = StateCode.IN

    def formula(tax_unit, period, parameters):
        # County calculations are at the person level for each taxpayer in the law
        in_in = tax_unit.household("state_code_str", period) == "IN"
        county = tax_unit.household("county_str", period)
        rate = np.zeros_like(county, dtype=float)
        rates = parameters(period).gov.states["in"].tax.income.county_rates
        rate[in_in] = rates[county[in_in]]
        return rate * tax_unit("in_agi", period)
