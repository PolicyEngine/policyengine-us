from policyengine_us.model_api import *


class md_flat_rate_county_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD flat rate county local income tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        county = tax_unit.household("county_str", period)
        taxable_income = tax_unit("md_taxable_income", period)

        p = parameters(period).gov.local.md.flat_rate
        flat_rate = p[county]

        # Progressive counties should not use flat rate
        is_anne_arundel = county == "ANNE_ARUNDEL_COUNTY_MD"
        is_frederick = county == "FREDERICK_COUNTY_MD"
        is_progressive_county = is_anne_arundel | is_frederick

        flat_rate_tax = flat_rate * taxable_income

        return where(is_progressive_county, 0, flat_rate_tax)
