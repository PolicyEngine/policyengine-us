from policyengine_us.model_api import *


class hi_ccap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Hawaii CCAP"
    definition_period = MONTH
    defined_for = StateCode.HI
    reference = "https://humanservices.hawaii.gov/bessd/files/2013/01/HAR-17-798.2-Child-Care-Services-Rules.pdf#page=14"

    def formula(spm_unit, period, parameters):
        has_eligible_child = add(spm_unit, period, ["hi_ccap_eligible_child"]) > 0
        income_eligible = spm_unit("hi_ccap_income_eligible", period)
        asset_eligible = spm_unit("is_ccdf_asset_eligible", period.this_year)
        activity_eligible = spm_unit("hi_ccap_activity_eligible", period)
        return has_eligible_child & income_eligible & asset_eligible & activity_eligible
