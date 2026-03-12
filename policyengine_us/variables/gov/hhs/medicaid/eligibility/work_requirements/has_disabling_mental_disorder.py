from policyengine_us.model_api import *


class has_disabling_mental_disorder(Variable):
    # criteria not yet defined by CMS, so treating as simple boolean for now
    value_type = bool
    entity = Person
    label = "Has a disabling mental health condition as defined for HR. 1"
    definition_period = YEAR
    reference = "https://www.congress.gov/bill/119th-congress/house-bill/1/text"
    default_value = False
