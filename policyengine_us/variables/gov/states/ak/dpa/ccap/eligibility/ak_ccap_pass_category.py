from policyengine_us.model_api import *


class AKCCAPPassCategory(Enum):
    PASS_II = "PASS II — post-ATAP transitional"
    PASS_III = "PASS III — general low-income"
    NONE = "Not eligible"


class ak_ccap_pass_category(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = AKCCAPPassCategory
    default_value = AKCCAPPassCategory.NONE
    definition_period = MONTH
    label = "Alaska CCAP PASS eligibility category"
    defined_for = StateCode.AK
    reference = (
        "https://casetext.com/regulation/alaska-administrative-code/title-7-health-and-social-services/part-1-administration/chapter-41-child-care-assistance-program/section-7-aac-41012-categories-of-assistance",
        "https://health.alaska.gov/media/igiccwuf/child-care-assistance-program-policies-and-procedures.pdf#page=144",
    )

    def formula(spm_unit, period):
        pass_2 = spm_unit("ak_ccap_pass_2_eligible", period)
        pass_3 = spm_unit("ak_ccap_pass_3_eligible", period)
        return select(
            [pass_2, pass_3],
            [
                AKCCAPPassCategory.PASS_II,
                AKCCAPPassCategory.PASS_III,
            ],
            default=AKCCAPPassCategory.NONE,
        )
