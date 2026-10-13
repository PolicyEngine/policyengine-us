from policyengine_us.model_api import *


class wi_cts_graduates_before_19(Variable):
    value_type = bool
    entity = Person
    label = "Wisconsin CTS student expected to graduate before age 19"
    definition_period = MONTH
    reference = "https://www.dhs.wisconsin.gov/publications/p23131-25-01.pdf#page=21"
