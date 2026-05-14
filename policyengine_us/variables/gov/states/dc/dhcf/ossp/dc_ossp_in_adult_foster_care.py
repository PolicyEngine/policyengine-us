from policyengine_us.model_api import *


class dc_ossp_in_adult_foster_care(Variable):
    value_type = bool
    entity = Person
    label = "Whether the person resides in an adult foster care home"
    definition_period = YEAR
    defined_for = StateCode.DC
    reference = "https://code.dccouncil.gov/us/dc/council/code/sections/4-205.49"
