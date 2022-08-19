from openfisca_us.model_api import *


class md_local_income_tax_before_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD local income tax before credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        county = tax_unit.household("county_str", period)
        in_md = tax_unit.household("state_code_str", period) == "MD"
        rate = np.zeros_like(county, dtype=float)
        rates = parameters(period).gov.local.tax.income.flat_tax_rate
        if in_md.sum() > 0:
            # Only compute Maryland local taxes if the simulation includes Maryland households.
            rate[in_md] = rates[county[in_md]]
        return rate * tax_unit("md_taxable_income", period)
