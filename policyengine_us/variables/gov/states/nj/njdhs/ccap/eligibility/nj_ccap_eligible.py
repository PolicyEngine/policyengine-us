from policyengine_us.model_api import *


class nj_ccap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for New Jersey CCAP"
    definition_period = MONTH
    defined_for = StateCode.NJ
    reference = (
        "https://www.nj.gov/humanservices/notices/documents/rules-and-regulations/NJAC%2010_15%20CHILD%20CARE%20SERVICES.PDF#page=52",
        "https://www.childcarenj.gov/ChildCareNJ/media/media_library/CCDF_State_Plan_for_New_Jersey_FFY25-27.pdf#page=14",
    )

    def formula(spm_unit, period, parameters):
        has_eligible_child = add(spm_unit, period, ["nj_ccap_eligible_child"]) > 0
        income_eligible = spm_unit("nj_ccap_income_eligible", period)
        asset_eligible = spm_unit("is_ccdf_asset_eligible", period.this_year)
        activity_eligible = spm_unit("nj_ccap_activity_eligible", period)
        person = spm_unit.members
        has_referred_child = spm_unit.any(
            person("nj_ccap_has_cpp_referral", period)
            & person("nj_ccap_eligible_child", period)
        )
        return asset_eligible & (
            (has_eligible_child & income_eligible & activity_eligible)
            | has_referred_child
        )
