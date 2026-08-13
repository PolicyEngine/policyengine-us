from policyengine_us.model_api import *


class wy_ccap_gross_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Wyoming CCAP gross income"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.WY
    reference = (
        "https://rules.wyo.gov/DownloadFile.aspx?source_id=24638&source_type_id=81&doc_type_id=110&include_meta_data=Y&file_type=pdf&filename=24638.pdf&token=189087205215053222164006221008072207044097222254",  # Wyo. Admin. Rules, DFS, Child Care - Purchase of Service, Ch. 1, Appendix B, eff. 05/07/2025 (PDF pp. 38-40)
        "https://dfs.wyo.gov/about/policy-manuals/child-care-subsidy-policy-manual/",  # Wyoming DFS Child Care Subsidy Policy Manual §901.G Table #1 (PDF pp. 2-4)
    )

    adds = "gov.states.wy.dfs.ccap.income.countable_income.sources"
