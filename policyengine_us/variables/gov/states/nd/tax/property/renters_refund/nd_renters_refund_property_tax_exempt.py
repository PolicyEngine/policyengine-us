from policyengine_us.model_api import *


class nd_renters_refund_property_tax_exempt(Variable):
    """Whether rent is paid for property-tax-exempt living quarters.

    This defaults to false because upstream inputs do not identify public
    housing, nursing home, or other property-tax-exempt quarters.
    """

    value_type = bool
    entity = TaxUnit
    label = "North Dakota Renter's Refund property is exempt from property tax"
    definition_period = YEAR
    reference = (
        "https://ndlegis.gov/cencode/t57c02.pdf#page=16",
        "https://www.tax.nd.gov/sites/www/files/documents/guidelines/homestead-veterans-renters/credits-for-nd-homeowners-renters-guideline.pdf#page=7",
    )
    defined_for = StateCode.ND
