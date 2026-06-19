from policyengine_us.model_api import *


class MNCCAPQualityRating(Enum):
    STAR_4 = "Four-star Parent Aware"
    ACCREDITED_OR_3STAR = "Accredited or three-star Parent Aware"
    NONE = "No quality differential"


class mn_ccap_quality_rating(Variable):
    value_type = Enum
    entity = Person
    possible_values = MNCCAPQualityRating
    default_value = MNCCAPQualityRating.NONE
    definition_period = MONTH
    label = "Minnesota CCAP provider quality rating"
    defined_for = StateCode.MN
    reference = (
        # Minn. Stat. 142E.17 subd. 4-5 — accreditation and Parent Aware
        # quality differentials.
        "https://www.revisor.mn.gov/statutes/cite/142E.17",
    )
