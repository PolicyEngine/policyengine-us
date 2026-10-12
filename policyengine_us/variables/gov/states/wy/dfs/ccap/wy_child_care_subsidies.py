from policyengine_us.model_api import *


class wy_child_care_subsidies(Variable):
    value_type = float
    entity = SPMUnit
    label = "Wyoming child care subsidies"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.WY
    reference = "https://rules.wyo.gov/DownloadFile.aspx?source_id=24638&source_type_id=81&doc_type_id=110&include_meta_data=Y&file_type=pdf&filename=24638.pdf&token=189087205215053222164006221008072207044097222254"  # Wyo. Admin. Rules, DFS, Child Care - Purchase of Service, Ch. 1, eff. 05/07/2025
    adds = ["wy_ccap"]
