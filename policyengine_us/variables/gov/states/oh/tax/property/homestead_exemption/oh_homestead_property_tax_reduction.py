from policyengine_us.model_api import *


class oh_homestead_property_tax_reduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio homestead property tax reduction"
    unit = USD
    definition_period = YEAR
    reference = "https://codes.ohio.gov/ohio-revised-code/section-323.152"
    defined_for = "oh_homestead_exemption_eligible"

    def formula(tax_unit, period, parameters):
        assessed_value = add(tax_unit, period, ["assessed_property_value"])
        return add(tax_unit, period, ["real_estate_taxes"]) * (
            tax_unit("oh_homestead_exemption", period) / max_(assessed_value, 1)
        )
