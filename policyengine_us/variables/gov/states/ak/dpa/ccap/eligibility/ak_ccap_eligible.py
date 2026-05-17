from policyengine_us.model_api import *


class ak_ccap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Alaska CCAP"
    definition_period = MONTH
    defined_for = StateCode.AK
    reference = (
        "https://casetext.com/regulation/alaska-administrative-code/title-7-health-and-social-services/part-1-administration/chapter-41-child-care-assistance-program/section-7-aac-41012-categories-of-assistance",
        "https://health.alaska.gov/media/igiccwuf/child-care-assistance-program-policies-and-procedures.pdf#page=173",
    )

    def formula(spm_unit, period):
        pass_2 = spm_unit("ak_ccap_pass_2_eligible", period)
        pass_3 = spm_unit("ak_ccap_pass_3_eligible", period)
        return pass_2 | pass_3
