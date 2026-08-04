from policyengine_us.model_api import *


class ks_ccap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Kansas CCAP"
    definition_period = MONTH
    defined_for = StateCode.KS
    reference = "https://content.dcf.ks.gov/ees/keesm/Current/keesm2810.htm"

    def formula(spm_unit, period, parameters):
        has_eligible_child = add(spm_unit, period, ["ks_ccap_eligible_child"]) > 0
        income_eligible = spm_unit("ks_ccap_income_eligible", period)
        asset_eligible = spm_unit("is_ccdf_asset_eligible", period.this_year)
        activity_eligible = spm_unit("ks_ccap_activity_eligible", period)
        return has_eligible_child & income_eligible & asset_eligible & activity_eligible
