from policyengine_us.model_api import *


class is_in_residential_care_facility(Variable):
    value_type = bool
    entity = Person
    label = "Whether the person lives in a residential care facility"
    definition_period = YEAR
