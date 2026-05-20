from policyengine_us.model_api import *


class nd_renters_refund_property_tax_exempt(Variable):
    value_type = bool
    entity = TaxUnit
    label = "North Dakota Renter's Refund property is exempt from property tax"
    definition_period = YEAR
    reference = "https://www.tax.nd.gov/renters-refund"
    defined_for = StateCode.ND
