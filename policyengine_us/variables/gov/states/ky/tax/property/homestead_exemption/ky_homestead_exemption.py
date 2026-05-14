from policyengine_us.model_api import *


class ky_homestead_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kentucky homestead exemption"
    unit = USD
    definition_period = YEAR
    reference = "https://revenue.ky.gov/Property/Residential-Farm-Commercial-Property/pages/homestead-exemption.aspx"
    defined_for = "ky_homestead_exemption_eligible"

    def formula(tax_unit, period, parameters):
        return min_(
            add(tax_unit, period, ["assessed_property_value"]),
            parameters(period).gov.states.ky.tax.property.homestead_exemption.amount,
        )
