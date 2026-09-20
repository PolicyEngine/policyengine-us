from policyengine_us.model_api import *


class de_poc_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Delaware Purchase of Care"
    definition_period = MONTH
    defined_for = StateCode.DE
    reference = "https://dhss.delaware.gov/wp-content/uploads/sites/2/dss/pdf/PurchaseofCareProviderHandbook_FINAL1_25_2023.pdf#page=79"

    def formula(spm_unit, period, parameters):
        has_eligible_child = add(spm_unit, period, ["de_poc_eligible_child"]) > 0
        income_eligible = spm_unit("de_poc_income_eligible", period)
        asset_eligible = spm_unit("is_ccdf_asset_eligible", period.this_year)
        activity_eligible = spm_unit("de_poc_activity_eligible", period)
        person = spm_unit.members
        has_referred_child = spm_unit.any(
            person("de_poc_has_dfs_referral", period)
            & person("de_poc_eligible_child", period)
        )
        return asset_eligible & (
            (has_eligible_child & income_eligible & activity_eligible)
            | has_referred_child
        )
