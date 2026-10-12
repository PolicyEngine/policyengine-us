from policyengine_us.model_api import *


class ak_ccap_copay(Variable):
    value_type = float
    entity = SPMUnit
    label = "Alaska CCAP family monthly copay"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.AK
    reference = "https://health.alaska.gov/media/igiccwuf/child-care-assistance-program-policies-and-procedures.pdf#page=203"

    def formula(spm_unit, period):
        # ATAP-enrolled families (PASS I) have a $0 copay per Manual §4040-3 D.
        # We use `is_tanf_enrolled` (PolicyEngine's family-level TANF/ATAP
        # enrollment flag) to break the circular dependency between
        # ak_ccap_copay -> ak_atap -> childcare_expenses -> ak_ccap.
        on_atap = spm_unit("is_tanf_enrolled", period)
        countable = spm_unit("ak_ccap_countable_income", period)
        rate = spm_unit("ak_ccap_copay_rate", period)
        return where(on_atap, 0, countable * rate)
