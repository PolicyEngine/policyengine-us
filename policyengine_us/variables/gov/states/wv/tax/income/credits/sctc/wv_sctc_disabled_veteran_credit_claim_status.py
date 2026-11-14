from policyengine_us.model_api import *


class WVSCTCDisabledVeteranCreditClaimStatus(Enum):
    NOT_CLAIMED = "Confirmed not claimed"
    CLAIMED = "Confirmed claimed"
    UNKNOWN = "Unknown"


class wv_sctc_disabled_veteran_credit_claim_status(Variable):
    """Actual current-year DV credit claim, not potential veteran eligibility."""

    value_type = Enum
    possible_values = WVSCTCDisabledVeteranCreditClaimStatus
    default_value = WVSCTCDisabledVeteranCreditClaimStatus.UNKNOWN
    entity = TaxUnit
    definition_period = YEAR
    label = "West Virginia disabled veteran property tax credit claim status"
    # PDF pages 11, 27, 36.
    reference = "https://tax.wv.gov/Documents/PIT/2025/it140.PersonalIncomeTaxFormsAndInstructions.2025.pdf#page=11"
    defined_for = StateCode.WV
