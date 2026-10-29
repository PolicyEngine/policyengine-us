from policyengine_us.model_api import *


class MTLIHEAPDwellingType(Enum):
    SINGLE_FAMILY = "Single family (house or modular)"
    MULTI_FAMILY = "Multi-family (apartment or duplex)"
    MOBILE_HOME = "Mobile home"
    NON_TRADITIONAL = "Non-traditional dwelling"


class mt_liheap_dwelling_type(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = MTLIHEAPDwellingType
    default_value = MTLIHEAPDwellingType.SINGLE_FAMILY
    definition_period = YEAR
    label = "Montana LIHEAP dwelling type"
    defined_for = StateCode.MT
    reference = (
        "https://rules.mt.gov/policy-library-documents/application/pdf/0074fe4c5989f116f77c281ac5736bf5b0f2facbfaf09daf76450ecad7fcdf47#page=1",
        "https://rules.mt.gov/policy-library-documents/application/pdf/b2add645c2eceddb643df5cdaf684339b968b43fc63b88f21ea882dfeb930366#page=1",
        # PDF pages 3-4
        "https://rules.mt.gov/policy-library-documents/application/pdf/325b36e5abb6a3bfa036c3802fc997ed50711b5407868ec8f4b61eabc538e3ed#page=3",
        # PDF pages 3-5
        "https://rules.mt.gov/policy-library-documents/application/pdf/fa158b2cdbf766e585e1fbf5811523e0dff4e760111590ae75d0456ee81551ad#page=3",
        # PDF pages 57, 74, 124
        "https://web.archive.org/web/20261015032646/https://dphhs.mt.gov/assets/hcsd/liheap/LIHEAPmanual.pdf#page=57",
    )
