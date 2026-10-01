from policyengine_us.model_api import *


class NYHEAPDwellingType(Enum):
    STANDARD = "Standard residence"
    ELIGIBLE_GROUP_RESIDENCE = (
        "HEAP-eligible group residence receiving the nominal payment"
    )
    INELIGIBLE_RESIDENCE = "HEAP-ineligible residence"


class ny_heap_dwelling_type(Variable):
    value_type = Enum
    possible_values = NYHEAPDwellingType
    default_value = NYHEAPDwellingType.STANDARD
    entity = SPMUnit
    definition_period = YEAR
    label = "New York HEAP dwelling arrangement"
    reference = "https://otda.ny.gov/programs/heap/HEAP-manual.pdf#page=45,46,47"
    documentation = "Eligible group residences are the treatment, enriched housing, supervised/supportive living and other settings listed in Chapter 8 F.3 (group living facilities must have at most 16 residents). Ineligible residences include private roomers/boarders, hotels, motels, vehicles, dormitories and congregate care under F.4. Ordinary subsidized housing uses the existing housing-assistance and heat-in-rent inputs."
