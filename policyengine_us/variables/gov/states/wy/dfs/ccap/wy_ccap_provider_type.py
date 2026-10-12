from policyengine_us.model_api import *


class WYCCAPProviderType(Enum):
    CENTER = "Child care center"
    LICENSED_FAMILY = "Licensed family setting"
    LEGALLY_EXEMPT = "Legally exempt provider"


class wy_ccap_provider_type(Variable):
    value_type = Enum
    entity = Person
    possible_values = WYCCAPProviderType
    default_value = WYCCAPProviderType.CENTER
    definition_period = MONTH
    defined_for = StateCode.WY
    label = "Wyoming CCAP child care provider type"
    reference = (
        "https://rules.wyo.gov/DownloadFile.aspx?source_id=24638&source_type_id=81&doc_type_id=110&include_meta_data=Y&file_type=pdf&filename=24638.pdf&token=189087205215053222164006221008072207044097222254",  # Wyo. Admin. Rules, DFS, Child Care - Purchase of Service, Ch. 1 §14, eff. 05/07/2025 (PDF p. 29)
        "https://dfs.wyo.gov/services/family-services/child-care/",  # Wyoming DFS Table I - Child Care Sliding Fee Scale, eff. 04/01/25-03/31/26 (single page)
    )
    # Table I rate columns: the licensed family setting covers family child
    # care homes and family child care centers; legally exempt covers
    # unlicensed relative and non-relative care. University, community
    # college, and Wind River Reservation centers receive the center rate
    # (Manual §1203.G).
