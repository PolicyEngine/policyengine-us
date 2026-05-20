from policyengine_us.model_api import *


class nd_renters_refund(Variable):
    value_type = float
    entity = TaxUnit
    label = "North Dakota Renter's Refund"
    unit = USD
    definition_period = YEAR
    reference = "https://www.tax.nd.gov/renters-refund"
    defined_for = "nd_renters_refund_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.nd.tax.property.renters_refund
        refund = max_(
            add(tax_unit, period, ["rent"]) * p.rent_rate
            - tax_unit("nd_renters_refund_income", period) * p.income_rate,
            0,
        )
        return min_(p.cap, max_(p.minimum, refund))
