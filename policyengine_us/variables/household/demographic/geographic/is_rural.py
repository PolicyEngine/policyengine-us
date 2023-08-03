from policyengine_us.model_api import *


class is_rural(Variable):
    value_type = bool
    entity = Household
    definition_period = YEAR
    label = "Is in a rural area"
    reference = "https://www.law.cornell.edu/cfr/text/47/54.505#b_3_i"
