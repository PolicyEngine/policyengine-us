from policyengine_us.model_api import *


class has_adl_impairment(Variable):
    # criteria not yet defined by CMS, so treating as simple boolean for now
    value_type = bool
    entity = Person
    label = "Is unable to perform 1 or more Activities of Daily Living"
    definition_period = YEAR
    reference = "https://www.congress.gov/bill/119th-congress/house-bill/1/text"
    default_value = False
