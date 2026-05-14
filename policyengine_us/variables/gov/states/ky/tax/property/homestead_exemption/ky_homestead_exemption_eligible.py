from policyengine_us.model_api import *


class ky_homestead_exemption_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Kentucky Homestead Exemption"
    definition_period = YEAR
    reference = "https://revenue.ky.gov/Property/Residential-Farm-Commercial-Property/pages/homestead-exemption.aspx"
    defined_for = StateCode.KY

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ky.tax.property.homestead_exemption
        person = tax_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        age = person("age", period.this_year)
        is_disabled = person("is_disabled", period)
        owns_assessed_property = add(tax_unit, period, ["assessed_property_value"]) > 0

        return (
            tax_unit.any(((age >= p.age_threshold) | is_disabled) & head_or_spouse)
            & owns_assessed_property
        )
