from policyengine_us.model_api import *


class in_county_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Indiana county tax"
    definition_period = YEAR
    unit = USD
    reference = (
        "https://iga.in.gov/laws/2024/ic/titles/6#6-3.6",
        "https://forms.in.gov/Download.aspx?id=16337#page=1",  # Schedule CT-40, line 3 (zero floor)
    )
    defined_for = StateCode.IN

    def formula(tax_unit, period, parameters):
        # County calculations are at the person level for each taxpayer in the law
        in_in = tax_unit.household("state_code_str", period) == "IN"
        county = tax_unit.household("county_str", period)
        safe_county = where(in_in & (county != "UNKNOWN"), county, "ADAMS_COUNTY_IN")
        rates = parameters(period).gov.states["in"].tax.income.county_rates
        in_valid_county = in_in & (county != "UNKNOWN")
        rate = np.zeros_like(county, dtype=float)
        rate[in_valid_county] = rates[safe_county[in_valid_county]]
        return rate * max_(0, tax_unit("in_agi", period))
