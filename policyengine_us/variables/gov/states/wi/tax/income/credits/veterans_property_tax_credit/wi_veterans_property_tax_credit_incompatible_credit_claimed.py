from policyengine_us.model_api import *


class wi_veterans_property_tax_credit_incompatible_credit_claimed(Variable):
    """Claimant or spouse actually claims an incompatible same-year credit.

    Includes School Property, Homestead or farmland preservation claims on this
    or another return that have not been removed by an effective amendment.
    Calculated alternative-credit potential is not an actual filed claim.
    VALID_CLAIM for a counterpart veterans claim plus true here is contradictory
    supplied data; the derived outputs do not adjudicate which filing prevails.
    """

    value_type = bool
    entity = TaxUnit
    label = "Wisconsin veterans property tax credit incompatible claim"
    definition_period = YEAR
    reference = (
        "https://docs.legis.wisconsin.gov/statutes/statutes/71/i/07/6e/c/2",
        # PDF pages 18, 27
        "https://www.revenue.wi.gov/TaxForms2025/2025-Form1-Inst.pdf#page=18",
    )
