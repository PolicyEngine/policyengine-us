from policyengine_us.model_api import *


class KYSSPCategory(Enum):
    PCH = "Personal Care Home"
    CIS = "Community Integration Supplementation"
    FCH = "Family Care Home"
    CARETAKER = "Caretaker Services"
    NONE = "None"


class ky_ssp_category(Variable):
    value_type = Enum
    entity = Person
    label = "Kentucky SSP category"
    definition_period = MONTH
    defined_for = StateCode.KY
    possible_values = KYSSPCategory
    default_value = KYSSPCategory.NONE
    reference = (
        "https://apps.legislature.ky.gov/law/kar/titles/921/002/015/",
        "https://www.chfs.ky.gov/agencies/dcbs/dfs/Documents/OMVOLV.pdf#page=23",
    )
