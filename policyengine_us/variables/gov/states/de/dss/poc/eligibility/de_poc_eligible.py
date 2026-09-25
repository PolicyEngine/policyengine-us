from policyengine_us.model_api import *


class de_poc_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Delaware Purchase of Care"
    definition_period = MONTH
    defined_for = StateCode.DE
    reference = "https://regulations.delaware.gov/AdminCode/title16/Department%20of%20Health%20and%20Social%20Services/Division%20of%20Social%20Services/11003.shtml"

    def formula(spm_unit, period, parameters):
        has_eligible_child = add(spm_unit, period, ["de_poc_eligible_child"]) > 0
        income_eligible = spm_unit("de_poc_income_eligible", period)
        asset_eligible = spm_unit("is_ccdf_asset_eligible", period.this_year)
        activity_eligible = spm_unit("de_poc_activity_eligible", period)
        return has_eligible_child & income_eligible & asset_eligible & activity_eligible
