from policyengine_us.model_api import *


class AKHAPDwellingType(Enum):
    LARGE_MOBILE_HOME_OR_BOAT = (
        "Mobile home or boat with at least 980 heated square feet"
    )
    RV_TENT_OR_CAMPER = "Recreational vehicle, tent, or pickup camper"
    STUDIO_HOTEL_OR_BOARDING_ROOM = "Studio apartment, hotel, or boarding room"
    SMALL_BOAT = "Boat with less than 980 heated square feet"
    ONE_BEDROOM_OR_ONE_ROOM_HOUSE = (
        "One-bedroom dwelling, or one-room house or cabin without bedrooms"
    )
    THREE_PLUS_BEDROOM_HOUSE = (
        "Three-or-more-bedroom single family, duplex, or triplex home"
    )
    TWO_BEDROOM_LARGE_APARTMENT_OR_SMALL_MOBILE = "Two-bedroom apartment in a building with four or more units, or mobile home below 980 heated square feet"
    TWO_BEDROOM_HOUSE = "Two-bedroom single family, duplex, or triplex home"


class ak_hap_dwelling_type(Variable):
    value_type = Enum
    possible_values = AKHAPDwellingType
    default_value = AKHAPDwellingType.TWO_BEDROOM_HOUSE
    entity = SPMUnit
    definition_period = YEAR
    label = "Alaska HAP dwelling type"
    reference = (
        "http://dpaweb.hss.state.ak.us/manuals/HAP/3004/3004-5_grant_computation.htm"
    )
    # Select the first matching category in the manual; a loft is a bedroom.
    # The neutral two-bedroom-house default is a modeling assumption, not a
    # state policy default. Unclassified dwellings require additional facts.
