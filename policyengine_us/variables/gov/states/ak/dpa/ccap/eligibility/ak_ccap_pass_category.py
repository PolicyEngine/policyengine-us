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
        "https://www.akleg.gov/statutesPDF/aac%20Title%207.pdf#page=846",
        "https://health.alaska.gov/media/igiccwuf/child-care-assistance-program-policies-and-procedures.pdf#page=145",
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
