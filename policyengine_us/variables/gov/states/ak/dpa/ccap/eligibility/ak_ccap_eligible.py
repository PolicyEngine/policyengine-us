from policyengine_us.model_api import *


class ak_ccap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Alaska CCAP"
    definition_period = MONTH
    defined_for = StateCode.AK
    reference = (
        "https://www.akleg.gov/statutesPDF/aac%20Title%207.pdf#page=846",
        "https://health.alaska.gov/media/igiccwuf/child-care-assistance-program-policies-and-procedures.pdf#page=173",
    )

    def formula(spm_unit, period):
        has_eligible_child = add(spm_unit, period, ["ak_ccap_child_eligible"]) > 0
        income_eligible = spm_unit("ak_ccap_income_eligible", period)
        asset_eligible = spm_unit("is_ccdf_asset_eligible", period.this_year)
        activity_eligible = spm_unit("ak_ccap_parent_in_eligible_activity", period)
        return has_eligible_child & income_eligible & asset_eligible & activity_eligible
