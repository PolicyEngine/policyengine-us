from policyengine_us.model_api import *


class nd_ccap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "North Dakota CCAP eligible"
    definition_period = MONTH
    defined_for = StateCode.ND
    reference = "https://www.nd.gov/dhs/policymanuals/40028/40028.htm"

    def formula(spm_unit, period, parameters):
        has_eligible_child = add(spm_unit, period, ["nd_ccap_eligible_child"]) > 0
        income_eligible = spm_unit("nd_ccap_income_eligible", period)
        # The $1,000,000 self-certified asset limit matches the federal CCDF
        # limit, so we reuse is_ccdf_asset_eligible (400-28-65-05).
        asset_eligible = spm_unit("is_ccdf_asset_eligible", period)
        activity_eligible = spm_unit("nd_ccap_activity_eligible", period)
        return has_eligible_child & income_eligible & asset_eligible & activity_eligible
