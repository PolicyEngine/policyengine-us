from policyengine_us.model_api import *


class sd_cca_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "South Dakota CCA eligible"
    definition_period = MONTH
    defined_for = StateCode.SD
    reference = "https://dss.sd.gov/docs/childcare/assistance/Subsidy_Manual.pdf#page=8"

    def formula(spm_unit, period, parameters):
        # The activity requirement is embedded per child through
        # sd_cca_reason_for_care_eligible inside sd_cca_eligible_child.
        has_eligible_child = add(spm_unit, period, ["sd_cca_eligible_child"]) > 0
        income_eligible = spm_unit("sd_cca_income_eligible", period)
        # The $1,000,000 self-certified asset limit matches the federal CCDF
        # limit, so we reuse is_ccdf_asset_eligible.
        asset_eligible = spm_unit("is_ccdf_asset_eligible", period)
        return has_eligible_child & income_eligible & asset_eligible
