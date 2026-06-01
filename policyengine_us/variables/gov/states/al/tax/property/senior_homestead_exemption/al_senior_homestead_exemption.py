from policyengine_us.model_api import *


class al_senior_homestead_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Alabama senior homestead exemption"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/alabama/title-40/chapter-9/article-1/section-40-9-19/",
        "https://www.revenue.alabama.gov/tax-types/property-ad-valorem-tax/",
        "https://www.revenue.alabama.gov/property-tax/homestead-exemptions/",
    )
    defined_for = "al_senior_homestead_exemption_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.al.tax.property.senior_homestead_exemption
        return min_(
            add(tax_unit, period, ["assessed_property_value"])
            * p.state_property_tax_rate,
            add(tax_unit, period, ["real_estate_taxes"]),
        )
