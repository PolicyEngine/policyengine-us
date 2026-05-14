from policyengine_us.model_api import *


class sc_homestead_property_tax_reduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "South Carolina homestead property tax reduction"
    unit = USD
    definition_period = YEAR
    reference = "https://dor.sc.gov/property/exempt-property"
    defined_for = "sc_homestead_exemption_eligible"

    def formula(tax_unit, period, parameters):
        assessed_value = add(tax_unit, period, ["assessed_property_value"])
        return add(tax_unit, period, ["real_estate_taxes"]) * (
            tax_unit("sc_homestead_exemption", period) / max_(assessed_value, 1)
        )
