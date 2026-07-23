from policyengine_us.model_api import *


class wy_ccap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Wyoming Child Care, Purchase of Service"
    definition_period = MONTH
    defined_for = StateCode.WY
    reference = (
        "https://rules.wyo.gov/DownloadFile.aspx?source_id=24638&source_type_id=81&doc_type_id=110&include_meta_data=Y&file_type=pdf&filename=24638.pdf&token=189087205215053222164006221008072207044097222254",  # Wyo. Admin. Rules, DFS, Child Care - Purchase of Service, Ch. 1 §8(e), eff. 05/07/2025 (PDF p. 16)
        "https://dfs.wyo.gov/about/policy-manuals/child-care-subsidy-policy-manual/",  # Wyoming DFS Child Care Subsidy Policy Manual §1101 (PDF p. 1)
    )

    def formula(spm_unit, period, parameters):
        # Rules Ch. 1 §8(e): the unit must include at least one eligible child
        # and meet the activity and income requirements. §8(f) considers no
        # resources in determining eligibility; only the federal CCDF
        # $1,000,000 asset ceiling applies (Manual §800). The eligibility bars
        # for fraud, fugitive felons, program noncooperation, and unpaid
        # overpayments (§8(e)(i)(F), (G), (L), (M)) are not modeled.
        has_eligible_child = add(spm_unit, period, ["wy_ccap_eligible_child"]) > 0
        income_eligible = spm_unit("wy_ccap_income_eligible", period)
        activity_eligible = spm_unit("wy_ccap_activity_eligible", period)
        asset_eligible = spm_unit("is_ccdf_asset_eligible", period.this_year)
        return has_eligible_child & income_eligible & activity_eligible & asset_eligible
