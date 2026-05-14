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
        assessed_value = add(tax_unit, period, ["assessed_property_value"])
        return add(tax_unit, period, ["real_estate_taxes"]) * (
            tax_unit("ky_homestead_exemption", period) / max_(assessed_value, 1)
        )
