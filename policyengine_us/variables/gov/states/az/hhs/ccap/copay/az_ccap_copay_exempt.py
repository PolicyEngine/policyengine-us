from policyengine_us.model_api import *


class az_ccap_copay_exempt(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Arizona Child Care Assistance Program copay exempt"
    definition_period = MONTH
    defined_for = StateCode.AZ
    reference = (
        "https://des.az.gov/sites/default/files/dl/CCA-0229AFY26.pdf#page=1",
        "https://des.az.gov/services/child-and-family/child-care/how-apply-for-child-care-assistance",
        "https://apps.azsos.gov/public_services/Title_06/6-05.pdf#page=33",
    )

    def formula(spm_unit, period, parameters):
        # R6-5-4915: the same families served without regard to income under
        # R6-5-4914(A) (DCS/DDD/foster referrals, Cash Assistance/Jobs families)
        # also have no fee or copayment.
        return spm_unit("az_ccap_categorically_eligible", period)
