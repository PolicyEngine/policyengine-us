from policyengine_us.model_api import *


class ms_age_disability_homestead_property_tax_reduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Mississippi age or disability homestead property tax reduction"
    unit = USD
    definition_period = YEAR
    reference = "https://www.dor.ms.gov/county-services/homestead-exemption"
    defined_for = "ms_age_disability_homestead_exemption_eligible"

    def formula(tax_unit, period, parameters):
        assessed_value = add(tax_unit, period, ["assessed_property_value"])
        return add(tax_unit, period, ["real_estate_taxes"]) * (
            tax_unit("ms_age_disability_homestead_exemption", period)
            / max_(assessed_value, 1)
        )
