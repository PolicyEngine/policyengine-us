from policyengine_us.model_api import *


class RICCAPStepRating(Enum):
    STEP_1 = "Step 1"
    STEP_2 = "Step 2"
    STEP_3 = "Step 3"
    STEP_4 = "Step 4"


class ri_ccap_step_rating(Variable):
    value_type = Enum
    entity = Person
    possible_values = RICCAPStepRating
    default_value = RICCAPStepRating.STEP_1
    definition_period = MONTH
    label = "Rhode Island CCAP license-exempt provider step rating"
    defined_for = StateCode.RI
    reference = "https://dhs.ri.gov/media/3556/download?language=en"
