from policyengine_us.model_api import *


class mn_homestead_credit_refund_property_taxes_available(Variable):
    value_type = bool
    entity = TaxUnit
    label = (
        "Minnesota Homestead Credit Refund qualified property tax amount is available"
    )
    definition_period = YEAR
    defined_for = StateCode.MN
    # Known zero and unavailable tax are distinct, regardless of legal eligibility.
    reference = (
        "https://www.revenue.state.mn.us/sites/default/files/2026-06/m1pr-25.pdf#page=2"
    )

    def formula_2025(tax_unit, period, parameters):
        return (
            tax_unit("mn_homestead_credit_refund_qualified_property_taxes", period) >= 0
        )
