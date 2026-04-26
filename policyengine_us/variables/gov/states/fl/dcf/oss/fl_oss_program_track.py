from policyengine_us.model_api import *


class FLOSSProgramTrack(Enum):
    REDESIGN = "Redesign"
    PROTECTED = "Protected"
    NONE = "None"


class fl_oss_program_track(Variable):
    value_type = Enum
    entity = Person
    label = "Florida OSS program track"
    definition_period = MONTH
    defined_for = StateCode.FL
    possible_values = FLOSSProgramTrack
    default_value = FLOSSProgramTrack.NONE
    reference = "https://www.myflfamilies.com/sites/default/files/2025-05/Appendix%20A-12%20-%20State%20Funded%20Programs%20Eligibility%20Standards.pdf"
