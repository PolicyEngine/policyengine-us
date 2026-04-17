from policyengine_us.model_api import *


class pa_ccw_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Pennsylvania CCW"
    definition_period = MONTH
    defined_for = StateCode.PA
    reference = "https://www.pacodeandbulletin.gov/secure/pacode/data/055/chapter3042/055_3042.pdf#page=9"

    def formula(spm_unit, period, parameters):
        has_eligible_child = (
            add(spm_unit, period.this_year, ["pa_ccw_eligible_child"]) > 0
        )
        income_eligible = spm_unit("pa_ccw_income_eligible", period)
        asset_eligible = spm_unit("is_ccdf_asset_eligible", period.this_year)
        activity_eligible = spm_unit("pa_ccw_activity_eligible", period.this_year)
        not_on_tanf = ~spm_unit("is_tanf_enrolled", period)
        return (
            has_eligible_child
            & income_eligible
            & asset_eligible
            & activity_eligible
            & not_on_tanf
        )
