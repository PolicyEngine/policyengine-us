from policyengine_us.model_api import *


class FLOSSCommunityCareType(Enum):
    ALF = "Assisted Living Facility"
    AFCH = "Adult Family Care Home"
    MHRTF = "Mental Health Residential Treatment Facility"
    NONE = "None"


class fl_oss_community_care_type(Variable):
    value_type = Enum
    entity = Person
    label = "Florida OSS community care facility type"
    definition_period = MONTH
    defined_for = StateCode.FL
    possible_values = FLOSSCommunityCareType
    default_value = FLOSSCommunityCareType.NONE
    reference = (
        "https://www.flrules.org/gateway/RuleNo.asp?title=PUBLIC%20ASSISTANCE&ID=65A-2.032",
        "https://www.myflfamilies.com/sites/default/files/2025-05/Appendix%20A-12%20-%20State%20Funded%20Programs%20Eligibility%20Standards.pdf",
    )
