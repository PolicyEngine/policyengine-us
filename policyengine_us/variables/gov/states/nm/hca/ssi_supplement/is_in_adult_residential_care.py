from policyengine_us.model_api import *


class is_in_adult_residential_care(Variable):
    value_type = bool
    entity = Person
    label = "Whether the person lives in a licensed adult residential shelter care home"
    definition_period = YEAR
    default_value = False
    reference = "https://srca.nm.gov/parts/title08/08.106.0100.html"
