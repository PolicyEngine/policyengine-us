from policyengine_us.model_api import *


class TNCCAPQRISTier(Enum):
    STATE_RATE = "State rate (no QRIS bonus)"
    QRIS_80_89 = "QRIS Scorecard 80-89"
    QRIS_90_100 = "QRIS Scorecard 90-100"


class tn_ccap_qris_tier(Variable):
    value_type = Enum
    entity = Person
    possible_values = TNCCAPQRISTier
    default_value = TNCCAPQRISTier.STATE_RATE
    definition_period = MONTH
    label = "Tennessee CCAP provider QRIS Scorecard tier"
    defined_for = StateCode.TN
    reference = "https://www.tn.gov/content/dam/tn/human-services/documents/Reimbursement_Rate_Chart_1.1.26.pdf"
