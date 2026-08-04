from policyengine_us.model_api import *


class mn_ccap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Minnesota CCAP"
    definition_period = MONTH
    defined_for = StateCode.MN
    reference = (
        # Minn. Rules 3400.0040, 3400.0170; Minn. Stat. 142E.
        "https://www.revisor.mn.gov/rules/3400/",
    )

    def formula(spm_unit, period, parameters):
        has_eligible_child = add(spm_unit, period, ["mn_ccap_eligible_child"]) > 0
        income_eligible = spm_unit("mn_ccap_income_eligible", period)
        asset_eligible = spm_unit("is_ccdf_asset_eligible", period.this_year)
        activity_eligible = spm_unit("mn_ccap_activity_eligible", period)
        return has_eligible_child & income_eligible & asset_eligible & activity_eligible
