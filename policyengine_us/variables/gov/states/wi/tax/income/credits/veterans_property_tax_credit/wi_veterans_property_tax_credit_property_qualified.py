from policyengine_us.model_api import *


class wi_veterans_property_tax_credit_property_qualified(Variable):
    """Known Wisconsin principal-property and lawful payment-route facts qualify.

    Supply the actual tenure, personal-use, allocation and effective-period
    facts, including proof of direct municipal payment for the narrow renter
    route. This flag does not establish timeliness or other claim permission.
    """

    value_type = bool
    entity = TaxUnit
    label = "Wisconsin veterans property tax credit qualified property"
    definition_period = YEAR
    reference = (
        "https://docs.legis.wisconsin.gov/statutes/statutes/71/i/07/6e",
        # PDF pages 28-30
        "https://www.revenue.wi.gov/TaxForms2025/2025-Form1-Inst.pdf#page=28",
    )
