from policyengine_us.model_api import *


class aca_zip3_ca_county_la(Variable):
    value_type = int
    entity = Household
    label = "ACA ZIP3 code for Los Angeles households expressed as an integer"
    definition_period = YEAR
    defined_for = StateCode.CA
    default_value = 900  # Los Angeles city
