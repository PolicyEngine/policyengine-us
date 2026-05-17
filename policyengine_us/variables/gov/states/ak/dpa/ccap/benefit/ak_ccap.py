from policyengine_us.model_api import *


class ak_ccap(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Alaska CCAP monthly benefit"
    definition_period = MONTH
    defined_for = "ak_ccap_eligible"
    reference = (
        "https://casetext.com/regulation/alaska-administrative-code/title-7-health-and-social-services/part-1-administration/chapter-41-child-care-assistance-program/section-7-aac-41012-categories-of-assistance",
        "https://health.alaska.gov/media/igiccwuf/child-care-assistance-program-policies-and-procedures.pdf#page=203",
    )

    def formula(spm_unit, period):
        total_per_child = add(spm_unit, period, ["ak_ccap_benefit_per_child"])
        copay = spm_unit("ak_ccap_copay", period)
        return max_(0, total_per_child - copay)
