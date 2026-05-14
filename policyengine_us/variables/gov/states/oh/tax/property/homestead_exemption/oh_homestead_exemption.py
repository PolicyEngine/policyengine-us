from policyengine_us.model_api import *


class oh_homestead_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio homestead exemption"
    unit = USD
    definition_period = YEAR
    reference = "https://codes.ohio.gov/ohio-revised-code/section-323.152"
    defined_for = "oh_homestead_exemption_eligible"

    def formula(tax_unit, period, parameters):
        return min_(
            add(tax_unit, period, ["assessed_property_value"]),
            parameters(period).gov.states.oh.tax.property.homestead_exemption.amount,
        )
