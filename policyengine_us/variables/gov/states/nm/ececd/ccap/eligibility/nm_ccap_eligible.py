from policyengine_us.model_api import *


class nm_ccap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for New Mexico CCAP"
    definition_period = MONTH
    defined_for = StateCode.NM
    reference = "https://www.srca.nm.gov/parts/title08/08.015.0002.html"

    def formula(spm_unit, period, parameters):
        has_eligible_child = add(spm_unit, period, ["nm_ccap_eligible_child"]) > 0
        income_eligible = spm_unit("nm_ccap_income_eligible", period)
        asset_eligible = spm_unit("is_ccdf_asset_eligible", period.this_year)
        activity_eligible = spm_unit("nm_ccap_activity_eligible", period)
        return has_eligible_child & income_eligible & asset_eligible & activity_eligible
