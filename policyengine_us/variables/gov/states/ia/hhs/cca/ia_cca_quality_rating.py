from policyengine_us.model_api import *


class IACCAQualityRating(Enum):
    RATING_1_OR_2 = "Quality Rating 1 or 2"
    RATING_3_OR_4 = "Quality Rating 3 or 4"
    RATING_5 = "Quality Rating 5"
    NO_RATING = "No Quality Rating"


class ia_cca_quality_rating(Variable):
    value_type = Enum
    entity = Person
    possible_values = IACCAQualityRating
    default_value = IACCAQualityRating.NO_RATING
    definition_period = MONTH
    label = "Iowa CCA provider quality rating"
    defined_for = StateCode.IA
    reference = "https://www.legis.iowa.gov/docs/iac/chapter/441.170.pdf#page=15"
