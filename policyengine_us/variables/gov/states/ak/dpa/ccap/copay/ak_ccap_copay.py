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
        countable = spm_unit("ak_ccap_countable_income", period)
        rate = spm_unit("ak_ccap_copay_rate", period)
        return countable * rate
