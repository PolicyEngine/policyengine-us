from policyengine_us.model_api import *


class OKCCSStarLevel(Enum):
    STAR_1 = "One star"
    STAR_2 = "Two star"
    STAR_3 = "Three star"
    STAR_4 = "Four star"
    STAR_5 = "Five star"


class ok_ccs_star_level(Variable):
    value_type = Enum
    entity = Person
    possible_values = OKCCSStarLevel
    default_value = OKCCSStarLevel.STAR_1
    definition_period = MONTH
    label = "Oklahoma Child Care Subsidy provider star level"
    defined_for = StateCode.OK
    reference = "https://oklahoma.gov/content/dam/ok/en/okdhs/documents/searchcenter/okdhsformresults/c-4-b.pdf#page=1"
