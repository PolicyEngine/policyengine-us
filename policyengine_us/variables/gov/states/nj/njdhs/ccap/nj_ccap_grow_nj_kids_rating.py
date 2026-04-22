from policyengine_us.model_api import *


class NJCCAPGrowNJKidsRating(Enum):
    NONE = "No Rating"
    STAR_3 = "3-Star"
    STAR_4 = "4-Star"
    STAR_5 = "5-Star"


class nj_ccap_grow_nj_kids_rating(Variable):
    value_type = Enum
    entity = Person
    possible_values = NJCCAPGrowNJKidsRating
    default_value = NJCCAPGrowNJKidsRating.NONE
    definition_period = MONTH
    label = "New Jersey CCAP Grow NJ Kids quality rating"
    defined_for = StateCode.NJ
    reference = "https://www.childcarenj.gov/ChildCareNJ/media/media_library/Max_CC_Payment_Rates.pdf#page=1"
