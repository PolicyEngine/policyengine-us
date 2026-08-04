from policyengine_us.model_api import *


class MICCAPStarRating(Enum):
    # STAR_1 holds both the Base Rate (blank star) and the 1 Star
    # (Maintaining Health & Safety) level, which carry identical rates.
    STAR_1 = "1 Star"
    STAR_2 = "2 Stars"
    STAR_3 = "3 Stars"
    STAR_4 = "4 Stars"
    STAR_5 = "5 Stars"


class mi_ccap_star_rating(Variable):
    value_type = Enum
    entity = Person
    possible_values = MICCAPStarRating
    default_value = MICCAPStarRating.STAR_1
    definition_period = MONTH
    label = "Michigan CDC licensed provider star quality level"
    defined_for = StateCode.MI
    reference = (
        "https://mdhhs-pres-prod.michigan.gov/olmweb/EX/RF/Public/RFT/270.pdf#page=4"
    )
