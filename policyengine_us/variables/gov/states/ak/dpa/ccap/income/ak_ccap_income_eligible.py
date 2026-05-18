from policyengine_us.model_api import *


class ak_ccap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Alaska CCAP based on income"
    definition_period = MONTH
    defined_for = StateCode.AK
    reference = (
        "https://www.akleg.gov/statutesPDF/aac%20Title%207.pdf#page=907",
        "https://health.alaska.gov/media/igiccwuf/child-care-assistance-program-policies-and-procedures.pdf#page=173",
    )

    def formula(spm_unit, period):
        countable = spm_unit("ak_ccap_countable_income", period)
        threshold = spm_unit("ak_ccap_smi_threshold", period)
        return countable <= threshold
