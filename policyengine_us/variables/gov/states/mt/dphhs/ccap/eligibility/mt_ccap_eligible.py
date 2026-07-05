from policyengine_us.model_api import *


class mt_ccap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Montana Best Beginnings Child Care Scholarship"
    definition_period = MONTH
    defined_for = StateCode.MT
    reference = (
        "https://www.law.cornell.edu/regulations/montana/Mont-Admin-r-37.80.201",
        "https://www.law.cornell.edu/regulations/montana/Mont-Admin-r-37.80.202",
    )

    def formula(spm_unit, period, parameters):
        # Modeled pathways: non-TANF income-eligible working families and
        # TANF cash-assistance families (via is_tanf_enrolled). Tribal,
        # tribal-TANF, and CFSD-referral pathways are not modeled at the moment
        # (no tribal-enrollment or CFSD-referral inputs).
        has_eligible_child = add(spm_unit, period, ["mt_ccap_eligible_child"]) > 0
        income_eligible = spm_unit("mt_ccap_income_eligible", period)
        asset_eligible = spm_unit("is_ccdf_asset_eligible", period.this_year)
        activity_eligible = spm_unit("mt_ccap_activity_eligible", period)
        return has_eligible_child & income_eligible & asset_eligible & activity_eligible
