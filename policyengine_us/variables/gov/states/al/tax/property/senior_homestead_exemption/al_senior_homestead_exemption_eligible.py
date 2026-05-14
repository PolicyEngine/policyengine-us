from policyengine_us.model_api import *


class al_senior_homestead_exemption_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Alabama senior homestead exemption"
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/alabama/title-40/chapter-9/article-1/section-40-9-19/",
        "https://www.law.cornell.edu/regulations/alabama/Ala-Admin-Code-r-810-4-1-.23",
        "https://www.revenue.alabama.gov/property-tax/homestead-exemptions/",
    )
    defined_for = StateCode.AL

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.al.tax.property.senior_homestead_exemption
        return (
            (tax_unit("greater_age_head_spouse", period) >= p.age_threshold)
            & (add(tax_unit, period, ["real_estate_taxes"]) > 0)
            & ~tax_unit("rents", period)
        )
