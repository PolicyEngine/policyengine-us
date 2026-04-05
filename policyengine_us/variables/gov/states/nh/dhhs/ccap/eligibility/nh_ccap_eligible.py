from policyengine_us.model_api import *


class nh_ccap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for New Hampshire Child Care Scholarship Program"
    definition_period = MONTH
    defined_for = StateCode.NH
    reference = "https://www.law.cornell.edu/regulations/new-hampshire/N-H-Admin-Code-SS-He-C-6910.07"

    def formula(spm_unit, period, parameters):
        has_eligible_child = add(spm_unit, period, ["nh_ccap_eligible_child"]) > 0
        income_eligible = spm_unit("nh_ccap_income_eligible", period)
        asset_eligible = spm_unit("is_ccdf_asset_eligible", period.this_year)
        activity_eligible = spm_unit("nh_ccap_activity_eligible", period)
        return has_eligible_child & income_eligible & asset_eligible & activity_eligible
