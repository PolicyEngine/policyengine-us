from policyengine_us.model_api import *


class me_ccap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Maine Child Care Affordability Program"
    definition_period = MONTH
    defined_for = StateCode.ME
    reference = "https://www.maine.gov/dhhs/sites/maine.gov.dhhs/files/inline-files/CCAP%20Full%20Rule%208.18.2025_1.pdf#page=11"

    def formula(spm_unit, period, parameters):
        has_eligible_child = add(spm_unit, period, ["me_ccap_eligible_child"]) > 0
        income_eligible = spm_unit("me_ccap_income_eligible", period)
        asset_eligible = spm_unit("is_ccdf_asset_eligible", period.this_year)
        activity_eligible = spm_unit("me_ccap_activity_eligible", period)
        return has_eligible_child & income_eligible & asset_eligible & activity_eligible
