from policyengine_us.model_api import *


class RICCAPStarRating(Enum):
    STAR_1 = "1 Star"
    STAR_2 = "2 Stars"
    STAR_3 = "3 Stars"
    STAR_4 = "4 Stars"
    STAR_5 = "5 Stars"


class ri_ccap_star_rating(Variable):
    value_type = Enum
    entity = Person
    possible_values = RICCAPStarRating
    default_value = RICCAPStarRating.STAR_1
    definition_period = MONTH
    label = "Rhode Island CCAP provider star rating"
    defined_for = StateCode.RI
    reference = "https://rules.sos.ri.gov/regulations/part/218-20-00-4#4.7.1"
