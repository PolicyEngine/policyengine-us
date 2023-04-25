from policyengine_us.model_api import *


class county_fips(Variable):
    value_type = int
    entity = Household
    definition_period = YEAR
    documentation = "County FIPS code"
