from policyengine_us.model_api import *


class KYSSPCareReceivers(Enum):
    ONE = "One spouse receives care"
    BOTH = "Both spouses receive care"


class ky_ssp_care_receivers(Variable):
    value_type = Enum
    entity = Person
    label = "Kentucky SSP caretaker couple care receivers"
    definition_period = MONTH
    defined_for = StateCode.KY
    possible_values = KYSSPCareReceivers
    default_value = KYSSPCareReceivers.ONE
    reference = (
        "https://apps.legislature.ky.gov/law/kar/titles/921/002/015/",
        "https://www.chfs.ky.gov/agencies/dcbs/dfs/Documents/OMVOLV.pdf#page=5",
    )
