from policyengine_us.model_api import *


class home_is_on_agricultural_land(Variable):
    value_type = bool
    entity = Person
    label = "Home is on agricultural land"
    definition_period = YEAR
    reference = "https://www.congress.gov/bill/119th-congress/house-bill/1/text"
