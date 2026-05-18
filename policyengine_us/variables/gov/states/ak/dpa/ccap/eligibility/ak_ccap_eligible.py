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
        pass_2 = spm_unit("ak_ccap_pass_2_eligible", period)
        pass_3 = spm_unit("ak_ccap_pass_3_eligible", period)
        return pass_2 | pass_3
