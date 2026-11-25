from policyengine_us.model_api import *


class WIVeteransPropertyTaxCreditSpouseClaimStatus(Enum):
    VALID_CLAIM = "Counterpart spouse has a verified valid same-year veterans claim"
    NOT_CLAIMED = "Counterpart spouse has no claim, including known absence of a spouse"
    UNKNOWN = "Counterpart spouse's claim status is unknown"


class wi_veterans_property_tax_credit_spouse_claim_status(Variable):
    """Verified same-taxable-year counterpart-spouse veterans claim status.

    Includes another return. VALID_CLAIM is a legally supported actual claim,
    not merely veteran status, an intended election or a positive amount.
    NOT_CLAIMED distinguishes known absence from missing cross-return facts.
    """

    value_type = Enum
    entity = TaxUnit
    label = "Wisconsin veterans property tax credit counterpart spouse claim"
    definition_period = YEAR
    possible_values = WIVeteransPropertyTaxCreditSpouseClaimStatus
    default_value = WIVeteransPropertyTaxCreditSpouseClaimStatus.UNKNOWN
    reference = (
        "https://docs.legis.wisconsin.gov/statutes/statutes/71/i/07/6e/c",
        # PDF pages 18, 27
        "https://www.revenue.wi.gov/TaxForms2025/2025-Form1-Inst.pdf#page=18",
    )
