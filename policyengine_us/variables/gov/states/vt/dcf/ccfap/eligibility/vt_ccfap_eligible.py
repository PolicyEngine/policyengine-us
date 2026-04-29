from policyengine_us.model_api import *


class vt_ccfap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    defined_for = StateCode.VT
    label = "Eligible for Vermont CCFAP"
    reference = (
        "https://outside.vermont.gov/dept/DCF/Shared%20Documents/CDD/CCFAP/CCFAP-Regulations.pdf#page=6",
        "https://legislature.vermont.gov/statutes/section/33/035/03512",
    )

    def formula(spm_unit, period, parameters):
        has_eligible_child = add(spm_unit, period, ["vt_ccfap_eligible_child"]) > 0
        asset_eligible = spm_unit("is_ccdf_asset_eligible", period.this_year)
        income_eligible = spm_unit("vt_ccfap_income_eligible", period)
        activity_eligible = spm_unit("vt_ccfap_meets_activity_test", period)
        categorically_exempt = spm_unit("vt_ccfap_categorically_exempt", period)

        return (
            has_eligible_child
            & asset_eligible
            & (activity_eligible | categorically_exempt)
            & (income_eligible | categorically_exempt)
        )
