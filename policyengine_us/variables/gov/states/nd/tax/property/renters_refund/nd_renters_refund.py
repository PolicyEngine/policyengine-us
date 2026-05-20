from policyengine_us.model_api import *


class nd_renters_refund(Variable):
    value_type = float
    entity = TaxUnit
    label = "North Dakota Renter's Refund"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://ndlegis.gov/cencode/t57c02.pdf#page=16",
        "https://www.tax.nd.gov/sites/www/files/documents/guidelines/homestead-veterans-renters/credits-for-nd-homeowners-renters-guideline.pdf#page=7",
    )
    defined_for = "nd_renters_refund_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.nd.tax.property.renters_refund
        # North Dakota excludes landlord-paid utilities and furnishings from
        # rent, but those amounts are not separated in current rent inputs.
        refund = (
            add(tax_unit, period, ["rent"]) * p.rent_rate
            - tax_unit("nd_renters_refund_income", period) * p.income_rate
        )
        return min_(p.cap, max_(p.minimum, refund))
