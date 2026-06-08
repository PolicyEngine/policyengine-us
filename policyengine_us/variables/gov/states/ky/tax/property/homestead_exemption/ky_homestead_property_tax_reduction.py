from policyengine_us.model_api import *


class ky_homestead_property_tax_reduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kentucky homestead property tax reduction"
    unit = USD
    definition_period = YEAR
    reference = "https://revenue.ky.gov/Property/Residential-Farm-Commercial-Property/pages/homestead-exemption.aspx"
    defined_for = "ky_homestead_exemption_eligible"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(period).gov.states.ky.tax.property.homestead_exemption
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        age = person("age", period.this_year)
        is_disabled = person("is_disabled", period)
        assessed_property_value = person("assessed_property_value", period)
        qualifying_owner = (
            ((age >= p.age_threshold) | is_disabled)
            & head_or_spouse
            & (assessed_property_value > 0)
        )
        qualifying_property_value = tax_unit.sum(
            where(qualifying_owner, assessed_property_value, 0)
        )
        qualifying_property_taxes = tax_unit.sum(
            where(qualifying_owner, person("real_estate_taxes", period), 0)
        )

        return qualifying_property_taxes * (
            tax_unit("ky_homestead_exemption", period)
            / max_(qualifying_property_value, 1)
        )
