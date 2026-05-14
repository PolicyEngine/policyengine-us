from policyengine_us.model_api import *


class sc_homestead_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "South Carolina homestead exemption"
    unit = USD
    definition_period = YEAR
    reference = "https://dor.sc.gov/property/exempt-property"
    defined_for = "sc_homestead_exemption_eligible"

    def formula(tax_unit, period, parameters):
        return min_(
            add(tax_unit, period, ["assessed_property_value"]),
            parameters(period).gov.states.sc.tax.property.homestead_exemption.amount,
        )
