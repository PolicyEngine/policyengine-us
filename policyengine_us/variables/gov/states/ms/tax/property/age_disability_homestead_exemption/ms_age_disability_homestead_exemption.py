from policyengine_us.model_api import *


class ms_age_disability_homestead_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Mississippi age or disability homestead exemption"
    unit = USD
    definition_period = YEAR
    reference = "https://www.dor.ms.gov/county-services/homestead-exemption"
    defined_for = "ms_age_disability_homestead_exemption_eligible"

    def formula(tax_unit, period, parameters):
        return min_(
            add(tax_unit, period, ["assessed_property_value"]),
            parameters(
                period
            ).gov.states.ms.tax.property.age_disability_homestead_exemption.amount,
        )
