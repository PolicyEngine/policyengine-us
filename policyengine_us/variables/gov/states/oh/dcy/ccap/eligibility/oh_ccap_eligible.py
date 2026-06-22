from policyengine_us.model_api import *


class oh_ccap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Ohio CCAP"
    definition_period = MONTH
    defined_for = StateCode.OH
    reference = (
        "https://codes.ohio.gov/ohio-administrative-code/rule-5180:2-16-01",
        "https://codes.ohio.gov/ohio-administrative-code/rule-5180:2-16-03",
        "https://dam.assets.ohio.gov/image/upload/childrenandyouth.ohio.gov/For%20Partners/Rules%20and%20Resources/2025/PL_21.pdf#page=2",
    )

    def formula(spm_unit, period, parameters):
        # Eligibility = income + child age + child citizenship + assets.
        #
        # We do not model the qualifying-activity (need-for-care) requirement
        # at the moment because its authorizing OAC rule (former 5101:2-16-02)
        # was rescinded with no current replacement. As a result this
        # over-grants relative to real policy, which requires every caretaker
        # to be in an approved activity (employment, education, training, or
        # job search). We also do not model the homeless or protective-service
        # eligibility bypasses, whose only authority is the same rescinded
        # rule; the copay waiver for those families (5180:2-16-05(G), still
        # in effect) is modeled separately in oh_ccap_copay.
        has_eligible_child = add(spm_unit, period, ["oh_ccap_eligible_child"]) > 0
        income_eligible = spm_unit("oh_ccap_income_eligible", period)
        # 5180:6-1-10 reuses the federal CCDF $1,000,000 asset cap, which is
        # effectively non-binding.
        asset_eligible = spm_unit("is_ccdf_asset_eligible", period.this_year)
        return has_eligible_child & income_eligible & asset_eligible
