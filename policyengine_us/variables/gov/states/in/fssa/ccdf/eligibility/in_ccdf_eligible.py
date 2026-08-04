from policyengine_us.model_api import *


class in_ccdf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Indiana CCDF eligible"
    definition_period = MONTH
    defined_for = StateCode.IN
    reference = "https://www.in.gov/fssa/carefinder/files/CCDF-Policy-Manual.pdf#page=5"

    def formula(spm_unit, period, parameters):
        income_eligible = spm_unit("in_ccdf_income_eligible", period)
        asset_eligible = spm_unit("in_ccdf_asset_eligible", period)
        activity_eligible = spm_unit("in_ccdf_activity_eligible", period)
        has_eligible_child = add(spm_unit, period, ["in_ccdf_eligible_child"]) > 0
        return income_eligible & asset_eligible & activity_eligible & has_eligible_child
