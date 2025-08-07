from policyengine_us.model_api import *


class in_out_of_home_care_facility(Variable):
    value_type = bool
    entity = Person
    label = "Is in a nonmedical out of home care facility"
    definition_period = YEAR
