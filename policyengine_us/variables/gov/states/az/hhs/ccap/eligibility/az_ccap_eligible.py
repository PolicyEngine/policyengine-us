from policyengine_us.model_api import *


class az_ccap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Arizona Child Care Assistance Program"
    definition_period = MONTH
    defined_for = StateCode.AZ
    reference = (
        "https://des.az.gov/services/child-and-family/child-care/how-apply-for-child-care-assistance",
        # R6-5-4914(A) Child Care Assistance Without Regard to Income
        "https://apps.azsos.gov/public_services/Title_06/6-05.pdf#page=29",
    )

    def formula(spm_unit, period, parameters):
        has_eligible_child = add(spm_unit, period, ["az_ccap_eligible_child"]) > 0
        income_eligible = spm_unit("az_ccap_income_eligible", period)
        # R6-5-4914(A): DCS/DDD/foster referrals and Cash Assistance/Jobs families
        # qualify without regard to income.
        categorically_eligible = spm_unit("az_ccap_categorically_eligible", period)
        asset_eligible = spm_unit("is_ccdf_asset_eligible", period.this_year)
        activity_eligible = spm_unit("az_ccap_activity_eligible", period)
        return (
            has_eligible_child
            & (income_eligible | categorically_eligible)
            & asset_eligible
            & activity_eligible
        )
