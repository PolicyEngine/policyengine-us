from policyengine_us.model_api import *


class wi_shares_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Wisconsin Shares eligible"
    definition_period = MONTH
    defined_for = StateCode.WI
    reference = (
        "https://dcf.wisconsin.gov/wisconsin-shares/wisconsin-shares-handbook-july-2026#page=22",
        "https://docs.legis.wisconsin.gov/statutes/statutes/49/III/155/1m",
    )

    def formula(spm_unit, period, parameters):
        # Wisconsin residency (Section 4.4) is enforced through the
        # defined_for = StateCode.WI gates on this eligibility chain.
        has_eligible_child = add(spm_unit, period, ["wi_shares_eligible_child"]) > 0
        income_eligible = spm_unit("wi_shares_income_eligible", period)
        asset_eligible = spm_unit("wi_shares_asset_eligible", period)
        activity_eligible = spm_unit("wi_shares_activity_eligible", period)
        return has_eligible_child & income_eligible & asset_eligible & activity_eligible
